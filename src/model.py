from transformers import pipeline

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Il tokenizer di questo modello non indica la lunghezza massima,
# quindi la impostiamo a mano: RoBERTa accetta al massimo 512 token
MAX_TOKEN = 512

# Il modello viene caricato una sola volta, quando il modulo viene importato,
# e non a ogni richiesta
classificatore = pipeline("text-classification", model=MODEL_NAME, top_k=None)


def predici_sentiment(testo: str) -> dict:
    """Restituisce l'etichetta più probabile e i punteggi di tutte e tre le classi."""
    risultati = classificatore(testo, truncation=True, max_length=MAX_TOKEN)[0]
    punteggi = {r["label"]: round(r["score"], 4) for r in risultati}
    migliore = max(risultati, key=lambda r: r["score"])
    return {
        "label": migliore["label"],
        "score": round(migliore["score"], 4),
        "scores": punteggi,
    }
