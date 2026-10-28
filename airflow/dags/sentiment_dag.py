"""Ciclo periodico di monitoraggio del modello di sentiment.

raccolta dati -> valutazione del modello -> decisione -> riaddestramento (o niente)

Airflow si occupa solo di orchestrare: le predizioni le fa l'API di sentiment,
che il DAG chiama via HTTP.
"""

import csv
import json
import os
import random
from datetime import datetime

import pendulum
import requests
from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.operators.empty import EmptyOperator

API_URL = os.environ.get("SENTIMENT_API_URL", "http://host.docker.internal:8000")
CARTELLA_DATI = "/opt/airflow/data"

# Dataset pubblico TweetEval: simula i commenti della settimana etichettati a mano
DATASET = (
    "https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment"
)
ETICHETTE = {"0": "negative", "1": "neutral", "2": "positive"}
DIMENSIONE_CAMPIONE = 200

# Sotto questa accuratezza il modello va riaddestrato
SOGLIA_ACCURATEZZA = float(os.environ.get("SOGLIA_ACCURATEZZA", "0.60"))


with DAG(
    dag_id="sentiment_monitoring",
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),
    schedule="@weekly",
    catchup=False,
    # un solo ciclo alla volta: due valutazioni insieme non avrebbero senso
    max_active_runs=1,
    tags=["sentiment", "mlops"],
) as dag:

    inizio = EmptyOperator(task_id="inizio")

    @task
    def raccogli_dati():
        """Scarica un campione di tweet etichettati e lo salva in un CSV."""
        testi = requests.get(f"{DATASET}/test_text.txt", timeout=60).text.splitlines()
        etichette = requests.get(
            f"{DATASET}/test_labels.txt", timeout=60
        ).text.splitlines()
        tweet = [(t, ETICHETTE[e.strip()]) for t, e in zip(testi, etichette)]
        campione = random.sample(tweet, DIMENSIONE_CAMPIONE)

        percorso = f"{CARTELLA_DATI}/campione_{datetime.now():%Y%m%d_%H%M%S}.csv"
        with open(percorso, "w", newline="", encoding="utf-8") as f:
            scrittore = csv.writer(f)
            scrittore.writerow(["text", "label"])
            scrittore.writerows(campione)
        # al task successivo passiamo solo il percorso, non i dati
        return percorso

    @task
    def valuta_modello(percorso):
        """Manda i testi all'API e calcola l'accuratezza rispetto alle etichette."""
        with open(percorso, encoding="utf-8") as f:
            righe = list(csv.DictReader(f))

        corretti = 0
        for riga in righe:
            risposta = requests.post(
                f"{API_URL}/predict", json={"text": riga["text"]}, timeout=30
            )
            risposta.raise_for_status()
            if risposta.json()["label"] == riga["label"]:
                corretti += 1

        accuratezza = corretti / len(righe)
        print(f"Accuratezza su {len(righe)} testi: {accuratezza:.1%}")
        return {"percorso": percorso, "n_testi": len(righe), "accuratezza": accuratezza}

    @task.branch
    def decidi_se_riaddestrare(risultati):
        if risultati["accuratezza"] < SOGLIA_ACCURATEZZA:
            print(f"Accuratezza sotto la soglia di {SOGLIA_ACCURATEZZA:.0%}")
            return "riaddestra_modello"
        print(f"Accuratezza sopra la soglia di {SOGLIA_ACCURATEZZA:.0%}")
        return "modello_ok"

    @task
    def riaddestra_modello(risultati):
        """Versione minima: registra la richiesta di riaddestramento.

        Un fine-tuning vero di RoBERTa richiederebbe una GPU e ore di calcolo,
        quindi andrebbe lanciato fuori da Airflow (ad esempio su un servizio di
        training) usando i dati raccolti.
        """
        richiesta = {
            "data": datetime.now().isoformat(timespec="seconds"),
            "motivo": f"accuratezza {risultati['accuratezza']:.1%} "
            f"sotto la soglia {SOGLIA_ACCURATEZZA:.0%}",
            "dati_di_addestramento": risultati["percorso"],
        }
        percorso = f"{CARTELLA_DATI}/richiesta_riaddestramento.json"
        with open(percorso, "w", encoding="utf-8") as f:
            json.dump(richiesta, f, indent=2)
        print(f"Richiesta di riaddestramento salvata in {percorso}")
        return percorso

    modello_ok = EmptyOperator(task_id="modello_ok")

    percorso_dati = raccogli_dati()
    risultati = valuta_modello(percorso_dati)
    decisione = decidi_se_riaddestrare(risultati)

    inizio >> percorso_dati
    decisione >> [riaddestra_modello(risultati), modello_ok]
