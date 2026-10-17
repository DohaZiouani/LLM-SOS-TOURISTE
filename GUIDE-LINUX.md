# SOS Tourist — LLM RAG : démarrage rapide (Linux)

Service RAG "Yasmine" : récupération sémantique (Qdrant + e5-large) + génération (Groq/LLaMA),
ancré sur le catalogue SOS Tourist.

## Pré-requis
- Python 3.10+  (`python3 --version`)
- Connexion internet (1er lancement : télécharge le modèle e5-large ~2 Go)

## Installation (1ère fois)

```bash
# 1. décompresser puis entrer dans le dossier
unzip sos-tourist-LLM.zip
cd sos-tourist-LLM

# 2. environnement Python isolé
python3 -m venv venv
source venv/bin/activate

# 3. dépendances
pip install -r requirements.txt

# 4. (clé Groq déjà incluse dans .env — rien à faire)
#    Pour utiliser ta propre clé :  nano .env

# 5. vérifier les 3 briques (télécharge e5-large ~2 Go la 1re fois)
python test_setup.py

# 6. indexer les 15 produits de démo (génère le dossier qdrant_data/)
python indexing/index_all.py

# 7. parler à Yasmine dans le terminal
python chat_cli.py
```

Pour quitter le chat : `Ctrl+C` (ou tape `q`).

## Exposer en API (optionnel, pour brancher la maquette/web)

```bash
uvicorn api:app --host 0.0.0.0 --port 8001
# test :
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"un riad à Marrakech ?"}'
```

## Questions de test
- « un riad à Marrakech »          → Riad Dar Salam
- « trek dans l'Atlas »            → Azur Expeditions
- « un trek au Mont Everest ? »    → refus poli (hors Maroc)
- « bghit chi riad f Marrakech »   → réponse en darija
