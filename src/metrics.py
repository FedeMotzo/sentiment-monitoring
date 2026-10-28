from prometheus_client import Counter, Histogram

# Metriche del servizio
RICHIESTE = Counter(
    "sentiment_requests_total",
    "Numero di richieste ricevute, per endpoint e status code",
    ["endpoint", "status"],
)
LATENZA = Histogram(
    "sentiment_request_latency_seconds",
    "Tempo di risposta delle richieste, in secondi",
    ["endpoint"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
)

# Metriche sul modello e sui testi in ingresso, utili per accorgersi del drift
PREDIZIONI = Counter(
    "sentiment_predictions_total",
    "Numero di predizioni per classe",
    ["label"],
)
CONFIDENZA = Histogram(
    "sentiment_prediction_confidence",
    "Punteggio della classe predetta",
    buckets=[0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1],
)
LUNGHEZZA_TESTO = Histogram(
    "sentiment_text_length_chars",
    "Lunghezza dei testi in ingresso, in caratteri",
    buckets=[10, 25, 50, 100, 200, 500, 1000, 2000],
)
