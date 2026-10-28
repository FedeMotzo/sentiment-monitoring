from src.model import predici_sentiment

CLASSI = {"positive", "neutral", "negative"}

FRASI_POSITIVE = [
    "I love this product, it works perfectly!",
    "What an amazing day, I'm so happy :)",
    "Great job guys, the new update is fantastic",
]

FRASI_NEGATIVE = [
    "This is the worst service I have ever used.",
    "I hate waiting hours for a refund that never arrives",
    "Terrible experience, the app keeps crashing",
]


def test_etichetta_sempre_tra_le_tre_classi():
    for testo in FRASI_POSITIVE + FRASI_NEGATIVE + ["The meeting is at 3pm", "ok", "?!"]:
        assert predici_sentiment(testo)["label"] in CLASSI


def test_punteggi_sommano_a_uno():
    risultato = predici_sentiment("Not sure what to think about this")
    assert set(risultato["scores"]) == CLASSI
    assert abs(sum(risultato["scores"].values()) - 1) < 0.01


def test_label_coerente_con_i_punteggi():
    risultato = predici_sentiment("I love this product, it works perfectly!")
    assert risultato["label"] == max(risultato["scores"], key=risultato["scores"].get)
    assert risultato["score"] == risultato["scores"][risultato["label"]]


def test_frasi_chiaramente_positive():
    for testo in FRASI_POSITIVE:
        assert predici_sentiment(testo)["label"] == "positive", testo


def test_frasi_chiaramente_negative():
    for testo in FRASI_NEGATIVE:
        assert predici_sentiment(testo)["label"] == "negative", testo


def test_testo_piu_lungo_di_512_token():
    # Prima della correzione con max_length=512 questo testo mandava in errore il modello
    risultato = predici_sentiment("word " * 1000)
    assert risultato["label"] in CLASSI


def test_stesso_testo_stesso_risultato():
    testo = "The service was fine, nothing special"
    assert predici_sentiment(testo) == predici_sentiment(testo)
