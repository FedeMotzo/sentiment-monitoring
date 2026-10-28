from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from src.app import app

client = TestClient(app)


def valore(nome, etichette=None):
    """Valore attuale di una metrica (0 se non è ancora stata registrata)."""
    return REGISTRY.get_sample_value(nome, etichette or {}) or 0


def test_endpoint_metrics():
    risposta = client.get("/metrics")
    assert risposta.status_code == 200
    assert "sentiment_requests_total" in risposta.text
    assert "sentiment_request_latency_seconds" in risposta.text


def test_predizione_aggiorna_le_metriche():
    prima_predizioni = valore("sentiment_predictions_total", {"label": "positive"})
    prima_richieste = valore(
        "sentiment_requests_total", {"endpoint": "/predict", "status": "200"}
    )
    prima_testi = valore("sentiment_text_length_chars_count")

    client.post("/predict", json={"text": "I love this, it's amazing!"})

    assert (
        valore("sentiment_predictions_total", {"label": "positive"})
        == prima_predizioni + 1
    )
    assert (
        valore("sentiment_requests_total", {"endpoint": "/predict", "status": "200"})
        == prima_richieste + 1
    )
    assert valore("sentiment_text_length_chars_count") == prima_testi + 1


def test_errori_contati_per_status_code():
    prima = valore(
        "sentiment_requests_total", {"endpoint": "/predict", "status": "422"}
    )
    client.post("/predict", json={"text": ""})
    assert (
        valore("sentiment_requests_total", {"endpoint": "/predict", "status": "422"})
        == prima + 1
    )


def test_metrics_non_conta_se_stesso():
    prima = valore(
        "sentiment_requests_total", {"endpoint": "/metrics", "status": "200"}
    )
    client.get("/metrics")
    assert (
        valore("sentiment_requests_total", {"endpoint": "/metrics", "status": "200"})
        == prima
    )
