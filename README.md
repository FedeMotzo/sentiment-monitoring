# Sentiment monitoring

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
- `POST /predict`: riceve `{"text": "..."}` e restituisce l'etichetta (`positive`, `neutral` o `negative`) con i punteggi delle tre classi.

La documentazione interattiva è su `http://127.0.0.1:8000/docs`. Per una prova veloce: `python scripts/prova_api.py`.

## Test

```bash
pytest
```

- `tests/test_api.py`: test dell'API (schema delle risposte, input vuoti, troppo lunghi o sbagliati);
- `tests/test_model.py`: test sul comportamento del modello (tre classi, frasi chiaramente positive e negative, testi più lunghi del limite del modello).

## Stile del codice

Il codice è formattato con **black** e controllato con **flake8** (configurazione in `.flake8`).

```bash
black .        # formatta il codice
flake8         # controlla lo stile
```
