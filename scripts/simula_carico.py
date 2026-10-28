"""Sovraccarica l'API con molte richieste lunghe in parallelo.

Serve per vedere salire la latenza in Grafana e far scattare l'alert
"Latenza alta su /predict" (95° percentile sopra 1 secondo per 2 minuti).
Uso: python scripts/simula_carico.py --secondi 210
"""

import argparse
import time
from concurrent.futures import ThreadPoolExecutor

import requests

TESTO_LUNGO = (
    "This product is good but the delivery was slow and support never answered. " * 26
)[:2000]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--secondi", type=int, default=210)
    parser.add_argument("--paralleli", type=int, default=20)
    args = parser.parse_args()

    def invia(_):
        requests.post(f"{args.url}/predict", json={"text": TESTO_LUNGO})

    fine = time.time() + args.secondi
    inviate = 0
    with ThreadPoolExecutor(args.paralleli) as esecutore:
        while time.time() < fine:
            list(esecutore.map(invia, range(args.paralleli)))
            inviate += args.paralleli
    print(f"Inviate {inviate} richieste in {args.secondi} secondi")


if __name__ == "__main__":
    main()
