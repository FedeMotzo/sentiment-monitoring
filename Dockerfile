FROM python:3.12-slim

WORKDIR /app

# Prima le dipendenze e poi il codice: se cambia solo il codice
# Docker riusa la cache e non reinstalla tutto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Il modello viene scaricato durante la build: il container parte subito
# e non ha bisogno di internet per funzionare
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='cardiffnlp/twitter-roberta-base-sentiment-latest')"

# Il modello è già nell'immagine: niente controlli online su Hugging Face all'avvio
ENV HF_HUB_OFFLINE=1

COPY src/ src/

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
