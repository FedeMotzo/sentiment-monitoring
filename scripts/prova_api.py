"""Prova a mano dell'API: va avviata prima con `uvicorn src.app:app`."""

import requests

URL = "http://127.0.0.1:8000"

risposta = requests.get(f"{URL}/health")
print("health:", risposta.status_code, risposta.json())

testi = [
    "I love this product, it works great!",
    "This is the worst service I have ever used.",
    "The meeting has been moved to 3pm.",
    "   ",
]
for testo in testi:
    risposta = requests.post(f"{URL}/predict", json={"text": testo})
    print(repr(testo), "->", risposta.status_code, risposta.json())
