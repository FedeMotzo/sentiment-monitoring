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
