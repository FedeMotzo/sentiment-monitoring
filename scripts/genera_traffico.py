"""Manda all'API dei tweet presi dal dataset pubblico TweetEval (sentiment).

Serve per generare traffico e vedere le metriche in Grafana.
Uso: python scripts/genera_traffico.py --n 200 --pausa 0.2
"""

import argparse
import random
import time

import requests

DATASET = (
    "https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment"
)
# nel dataset le etichette sono numeri
ETICHETTE = {"0": "negative", "1": "neutral", "2": "positive"}


def scarica_tweet():
    testi = requests.get(f"{DATASET}/test_text.txt").text.splitlines()
    etichette = requests.get(f"{DATASET}/test_labels.txt").text.splitlines()
    return [(t, ETICHETTE[e.strip()]) for t, e in zip(testi, etichette)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--n", type=int, default=200, help="numero di tweet da inviare")
    parser.add_argument(
        "--pausa", type=float, default=0.2, help="secondi tra due invii"
    )
    args = parser.parse_args()

    tweet = random.sample(scarica_tweet(), args.n)
    corretti = 0
    for i, (testo, vera) in enumerate(tweet, start=1):
        risposta = requests.post(f"{args.url}/predict", json={"text": testo})
        if risposta.status_code == 200 and risposta.json()["label"] == vera:
            corretti += 1
        if i % 50 == 0:
            print(f"{i} tweet inviati, accuratezza finora {corretti / i:.1%}")
        time.sleep(args.pausa)

    print(f"Fine: {args.n} tweet, accuratezza {corretti / args.n:.1%}")


if __name__ == "__main__":
    main()
