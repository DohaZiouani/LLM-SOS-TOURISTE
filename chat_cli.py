"""Petit chat en ligne de commande qui utilise l'orchestrateur. Quitter : 'q'."""
from dotenv import load_dotenv
load_dotenv()
from orchestrateur import repondre

print("Yasmine — SOS Tourist (tape 'q' pour quitter)\n")
while True:
    try:
        q = input("Vous › ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if q.lower() in ("q", "quit", "exit"):
        break
    if not q:
        continue
    print("Yasmine ›", repondre(q, verbose=False), "\n")
