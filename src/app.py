from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.model import MODEL_NAME, predici_sentiment

# Lunghezza massima del testo accettato, in caratteri
MAX_CARATTERI = 2000

app = FastAPI(title="Sentiment API")


class Testo(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_CARATTERI)


class Predizione(BaseModel):
    label: str
    score: float
    scores: dict[str, float]


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}


# def e non async def: la predizione impegna la CPU e FastAPI
# la esegue in un thread separato senza bloccare le altre richieste
@app.post("/predict", response_model=Predizione)
def predict(dati: Testo):
    if not dati.text.strip():
        raise HTTPException(status_code=400, detail="Il testo non può essere vuoto")
    return predici_sentiment(dati.text)
