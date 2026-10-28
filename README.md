# Sentiment monitoring

![CI/CD](https://github.com/FedeMotzo/sentiment-monitoring/actions/workflows/ci-cd.yml/badge.svg)

Progetto finale del modulo "MLOps e Machine Learning in produzione".

L'obiettivo è costruire un servizio che classifica il sentiment dei testi social (positivo, neutro, negativo) usando il modello pre-addestrato [twitter-roberta-base-sentiment-latest](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest) e portarlo "in produzione": API, test, Docker, CI/CD, monitoraggio e orchestrazione.

## Ambiente

Il progetto usa Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Avviare l'API

```bash
uvicorn src.app:app --reload
```

Al primo avvio il modello viene scaricato da Hugging Face (circa 500 MB).

Endpoint:
- `GET /health`: controlla che il servizio sia attivo;
- `POST /predict`: riceve `{"text": "..."}` e restituisce l'etichetta (`positive`, `neutral` o `negative`) con i punteggi delle tre classi;
- `GET /metrics`: metriche del servizio nel formato di Prometheus (richieste, latenza, classi predette, confidenza, lunghezza dei testi).

La documentazione interattiva è su `http://127.0.0.1:8000/docs`. Per una prova veloce: `python scripts/prova_api.py`.

## Docker

```bash
docker build -t sentiment-api .
docker run -p 8000:8000 sentiment-api
```

Il modello viene scaricato durante la build, quindi il container parte in pochi secondi e funziona anche senza internet.

## Monitoraggio

Con Docker Compose si avviano insieme l'API, Prometheus (che raccoglie le metriche da `/metrics` ogni 5 secondi) e Grafana (già collegato a Prometheus).

```bash
docker compose up -d --build
```

- API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (utente `admin`, password `admin`)

Per generare un po' di traffico con tweet reali del dataset pubblico [TweetEval](https://github.com/cardiffnlp/tweeteval):

```bash
python scripts/genera_traffico.py --n 200
```

In Grafana la dashboard **Sentiment API** (cartella *Sentiment*) è già pronta. Mostra:
- **servizio:** API raggiungibile, richieste al secondo, latenza, errori;
- **modello e dati:** classi predette, confidenza media, lunghezza dei testi.

Alert configurati (menu *Alerting → Alert rules*):

| Alert | Condizione |
|---|---|
| API non raggiungibile | Prometheus non legge l'API per 1 minuto |
| Latenza alta su /predict | 95° percentile sopra 1 secondo per 2 minuti |
| Troppi errori del servizio | errori 5xx sopra il 5% delle richieste per 5 minuti |

Per vedere scattare l'alert sulla latenza: `python scripts/simula_carico.py` (circa 3 minuti e mezzo). Per quello sull'API basta fermarla: `docker compose stop api`.

## Orchestrazione con Airflow

Il DAG `airflow/dags/sentiment_dag.py` descrive il ciclo settimanale di controllo del modello:

```
inizio → raccogli_dati → valuta_modello → decidi_se_riaddestrare ─┬→ riaddestra_modello
                                                                   └→ modello_ok
```

1. **raccogli_dati**: scarica un campione di 200 tweet etichettati (TweetEval) e lo salva in `airflow/data/`;
2. **valuta_modello**: manda i testi all'API e calcola l'accuratezza;
3. **decidi_se_riaddestrare**: se l'accuratezza è sotto la soglia (60%) va al riaddestramento, altrimenti a `modello_ok`;
4. **riaddestra_modello**: versione minima, salva una richiesta di riaddestramento con i dati raccolti.

Per avviarlo serve l'API attiva (`docker compose up -d` nella cartella principale), poi:

```bash
cd airflow
echo -e "AIRFLOW_UID=$(id -u)" > .env
docker compose up airflow-init
docker compose up -d
```

Interfaccia su http://localhost:8080 (utente `airflow`, password `airflow`). Il DAG si chiama `sentiment_monitoring`.

Per provare il ramo del riaddestramento si può alzare la soglia, con il DAG in pausa (altrimenti anche lo scheduler esegue gli stessi task):

```bash
docker compose exec -e SOGLIA_ACCURATEZZA=0.95 airflow-scheduler airflow dags test sentiment_monitoring
```

## Test

```bash
pytest
```

- `tests/test_api.py`: test dell'API (schema delle risposte, input vuoti, troppo lunghi o sbagliati);
- `tests/test_model.py`: test sul comportamento del modello (tre classi, frasi chiaramente positive e negative, testi più lunghi del limite del modello);
- `tests/test_metrics.py`: test delle metriche esposte su `/metrics`.

## CI/CD

Il workflow `.github/workflows/ci-cd.yml` ha due job:
- **test** (a ogni push): flake8, controllo di black e pytest;
- **build-and-push-image** (solo su `main`, se i test passano): costruisce l'immagine Docker e la pubblica su GitHub Packages.

```bash
docker pull ghcr.io/fedemotzo/sentiment-monitoring:main
docker run -p 8000:8000 ghcr.io/fedemotzo/sentiment-monitoring:main
```

## Stile del codice

Il codice è formattato con **black** e controllato con **flake8** (configurazione in `.flake8`).

```bash
black .        # formatta il codice
flake8         # controlla lo stile
```
