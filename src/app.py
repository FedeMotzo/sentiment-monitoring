import time

from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from src.metrics import CONFIDENZA, LATENZA, LUNGHEZZA_TESTO, PREDIZIONI, RICHIESTE
from src.model import MODEL_NAME, predici_sentiment

# Lunghezza massima del testo accettato, in caratteri
MAX_CARATTERI = 2000

# Endpoint di cui registriamo richieste e latenza
ENDPOINT_MONITORATI = {"/predict", "/health"}

app = FastAPI(title="Sentiment API")


class Testo(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_CARATTERI)


class Predizione(BaseModel):
    label: str
    score: float
    scores: dict[str, float]


# Viene eseguito per ogni richiesta: misura il tempo di risposta e conta
# le richieste per status code (compresi gli errori 4xx e 5xx)
@app.middleware("http")
async def registra_metriche(request: Request, call_next):
    inizio = time.perf_counter()
    risposta = await call_next(request)
    endpoint = request.url.path
    if endpoint in ENDPOINT_MONITORATI:
        LATENZA.labels(endpoint=endpoint).observe(time.perf_counter() - inizio)
        RICHIESTE.labels(endpoint=endpoint, status=risposta.status_code).inc()
    return risposta


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}


# def e non async def: la predizione impegna la CPU e FastAPI
# la esegue in un thread separato senza bloccare le altre richieste
@app.post("/predict", response_model=Predizione)
def predict(dati: Testo):
    if not dati.text.strip():
        raise HTTPException(status_code=400, detail="Il testo non può essere vuoto")
    risultato = predici_sentiment(dati.text)
    PREDIZIONI.labels(label=risultato["label"]).inc()
    CONFIDENZA.observe(risultato["score"])
    LUNGHEZZA_TESTO.observe(len(dati.text))
    return risultato


# Endpoint letto da Prometheus per raccogliere le metriche
@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
