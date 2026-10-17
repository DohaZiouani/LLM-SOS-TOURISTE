# SOS Tourist — LLM (RAG multi-agents)

Composante IA de SOS Tourist : un assistant touristique **Yasmine** bâti sur une
architecture **RAG multi-agents**, dans le même esprit qu'enjoy212, mais avec les
données et les domaines de SOS Tourist.

- **Embeddings** : `intfloat/multilingual-e5-large` (1024 dim), en local
- **Base vectorielle** : Qdrant en mode local (dossier `qdrant_data/`, aucun serveur à lancer)
- **LLM** : Groq → `llama-3.1-8b-instant` (interchangeable)
- **Récupération sémantique** : trouve les produits pertinents parmi *tout* le
  catalogue (≠ « 12 premiers » figés), puis ne donne que ceux-là au LLM.

## 🏗️ Architecture

```
                    Question du voyageur
                            │
                   ┌────────▼─────────┐
                   │  orchestrateur   │  ← « LLM Global » : route vers le bon domaine
                   │ (mots-clés + LLM)│
                   └───┬───┬───┬───┬──┘
        ┌──────────────┘   │   │   └──────────────┐
        ▼                  ▼   ▼                   ▼
  agent_hebergement  agent_restauration  agent_activites  agent_artisanat
        │                  │   │                   │
        ▼                  ▼   ▼                   ▼          (chaque agent = RAG)
   collection         collection          collection     collection   ← Qdrant
   "hebergement"      "restauration"      "activites"     "artisanat"
        └──────────────── e5-large (embeddings) ─────────────────┘
                            │
                          Groq (Llama 3.1) → réponse
```

4 domaines (adaptés au catalogue SOS Tourist) :

| Domaine | `typeProduit` indexés | Exemples |
|---|---|---|
| `hebergement` | Hotel, Riad, Gite | Riad Dar Salam, Chambre vue mer |
| `restauration` | Restaurant | Dîner Dar Moha |
| `activites` | Activitie, Event | Trek Atlas, Surf, Bivouac, Festival des Gnaouas |
| `artisanat` | Artisanat | Huile d'argan, Coffret découverte |

## 🚀 Setup (une seule fois)

```bash
# 1. (recommandé) environnement virtuel
python3 -m venv venv && source venv/bin/activate

# 2. dépendances
pip install -r requirements.txt

# 3. configuration
cp .env.example .env        # puis mets ta clé GROQ_API_KEY (gratuite : console.groq.com)

# 4. vérifier les 3 briques (Groq + Qdrant + embeddings)
python test_setup.py
```

> ⚠️ Au 1er lancement, `sentence-transformers` télécharge le modèle e5-large
> (~2 Go) depuis Hugging Face — prévois quelques minutes et une connexion internet.

## 📦 Indexation (transformer le catalogue en vecteurs)

```bash
python indexing/index_all.py        # indexe les 4 domaines d'un coup
# ou un par un :
python indexing/index_hebergement.py
python indexing/index_restauration.py
python indexing/index_activites.py
python indexing/index_artisanat.py
```

Les données viennent de `produitService_dataset.json` (mêmes champs que ta base
MongoDB SOS Tourist). **Pour passer à tes 607 produits réels**, exporte ta
collection `produitService` dans ce fichier (ou adapte `DATASET_PATH` dans `.env`)
et relance l'indexation.

## 💬 Utilisation

```bash
# Tester les 4 agents + l'orchestrateur
python test_agents.py

# Chat interactif en ligne de commande
python chat_cli.py

# Interroger un seul agent
python agents/agent_activites.py

# Orchestrateur (routage automatique)
python orchestrateur.py "Je cherche un riad calme à Marrakech"
```

## 🌐 Exposer en API (pour brancher sur Yasmine / Express)

```bash
uvicorn api:app --host 0.0.0.0 --port 8001
```
puis :
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"un trek dans l_Atlas ?"}'
# → { "reply": "..." }
```

**Branchement sur ton app MEAN :** ta route Express `POST /api/chat` (celle du
widget Yasmine) appelle ce service au lieu de coller un bloc figé dans le prompt :

```js
// dans routes/chat.js — au lieu de buildSystemContext()
const r = await fetch("http://localhost:8001/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ question: messages.at(-1).content }),
});
const { reply } = await r.json();
return res.json({ reply });
```
Le widget Angular et le reste de Yasmine ne changent pas — seul le « cerveau » derrière.

## 📁 Structure

```
sos-tourist-LLM/
├── core_rag.py                 # cœur partagé : embeddings + Qdrant + Groq + RAG
├── orchestrateur.py            # LLM Global : route la question vers le bon agent
├── api.py                      # service FastAPI (POST /chat) — pont avec Express
├── chat_cli.py                 # chat interactif en terminal
├── build_dataset.py            # (re)génère le dataset depuis le catalogue
├── produitService_dataset.json # catalogue SOS Tourist (à remplacer par ton export)
├── indexing/                   # un indexeur par domaine + index_all.py
├── agents/                     # un agent expert par domaine
├── test_setup.py               # vérifie Groq + Qdrant + embeddings
├── test_agents.py              # teste les agents + l'orchestrateur
├── requirements.txt
└── .env.example
```

## 🔄 Notes

- **Changer de LLM** (ex. Claude/Anthropic) : il suffit d'adapter `ask_llm()` dans
  `core_rag.py` (~3 lignes). Le reste du RAG ne bouge pas.
- **Darija / arabe** : e5-large est multilingue (gère FR/AR). Pour pousser le darija
  comme le demande le CDC, on pourra ajouter un index/embedding dédié plus tard.
- **Qdrant cloud** : remplace `QdrantClient(path=...)` par
  `QdrantClient(url=..., api_key=...)` si tu préfères un Qdrant hébergé.
