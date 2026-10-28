from fastapi.testclient import TestClient

from src.app import MAX_CARATTERI, app

client = TestClient(app)

CLASSI = {"positive", "neutral", "negative"}


def test_health():
    risposta = client.get("/health")
    assert risposta.status_code == 200
    assert risposta.json()["status"] == "ok"
    assert "model" in risposta.json()


def test_predict_schema_della_risposta():
    risposta = client.post("/predict", json={"text": "I really like this new phone"})
    assert risposta.status_code == 200
    dati = risposta.json()
    assert set(dati) == {"label", "score", "scores"}
    assert dati["label"] in CLASSI
    assert isinstance(dati["score"], float)
    assert 0 <= dati["score"] <= 1
    assert set(dati["scores"]) == CLASSI


def test_predict_testo_vuoto():
    risposta = client.post("/predict", json={"text": ""})
    assert risposta.status_code == 422


def test_predict_solo_spazi():
    risposta = client.post("/predict", json={"text": "    "})
    assert risposta.status_code == 400
    assert risposta.json()["detail"] == "Il testo non può essere vuoto"


def test_predict_testo_troppo_lungo():
    risposta = client.post("/predict", json={"text": "a" * (MAX_CARATTERI + 1)})
    assert risposta.status_code == 422


def test_predict_testo_lungo_al_limite():
    # Testo valido ma più lungo dei 512 token del modello: deve essere troncato, non dare errore
    risposta = client.post("/predict", json={"text": "a " * (MAX_CARATTERI // 2)})
    assert risposta.status_code == 200
    assert risposta.json()["label"] in CLASSI


def test_predict_campo_mancante():
    risposta = client.post("/predict", json={"testo": "campo con il nome sbagliato"})
    assert risposta.status_code == 422


def test_predict_metodo_sbagliato():
    risposta = client.get("/predict")
    assert risposta.status_code == 405
