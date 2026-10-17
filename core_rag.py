"""
core_rag.py — cœur partagé du RAG SOS Tourist (même approche qu'enjoy212).

Briques :
  - Embeddings : intfloat/multilingual-e5-large (1024 dim), en local via sentence-transformers
  - Base vectorielle : Qdrant en mode local (dossier ./qdrant_data, aucun serveur à lancer)
  - LLM : Groq (llama-3.1-8b-instant) — interchangeable

Tout est factorisé ici (un seul chargement du modèle, partagé par tous les agents)
au lieu d'être dupliqué dans chaque fichier. Les chemins sont résolus par rapport à
ce fichier, donc les scripts marchent quel que soit le répertoire courant.
"""
import os
import json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv()

_BASE = os.path.dirname(os.path.abspath(__file__))
_DATA = os.path.join(_BASE, "..", "sos-tourist", "DATA")
QDRANT_PATH = os.getenv("QDRANT_PATH", os.path.join(_BASE, "qdrant_data"))
DATASET_PATH = os.getenv("DATASET_PATH", os.path.join(_BASE, "produitService_dataset.json"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-large")
EMBED_DIM = 1024
LLM_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# --- Singletons (chargés à la première utilisation) ---
_encoder = None
_qdrant = None
_groq = None


def get_encoder():
    global _encoder
    if _encoder is None:
        from sentence_transformers import SentenceTransformer
        print(f"[core] Chargement du modèle d'embeddings « {EMBED_MODEL} » (1re fois, ~1-2 min)…")
        _encoder = SentenceTransformer(EMBED_MODEL)
    return _encoder


def get_qdrant():
    global _qdrant
    if _qdrant is None:
        _qdrant = QdrantClient(path=QDRANT_PATH)
    return _qdrant


def get_groq():
    global _groq
    if _groq is None:
        from groq import Groq
        _groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _groq


# --- Embeddings (conventions E5 : "passage:" à l'indexation, "query:" à la recherche) ---
def embed_passage(text):
    return get_encoder().encode(f"passage: {text}").tolist()


def embed_query(text):
    return get_encoder().encode(f"query: {text}").tolist()


# --- Chargement + filtrage du dataset par type de produit ---
def load_products(types):
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for item in data:
        if item.get("typeProduit") in types:
            tr = next((t for t in item.get("translations", []) if t.get("language") == "fr"), None)
            if tr:
                rows.append((item, tr))
    return rows


# --- Indexation d'un domaine dans sa collection Qdrant ---
def index_domain(collection, types):
    client = get_qdrant()
    if client.collection_exists(collection):
        client.delete_collection(collection)
    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )

    rows = load_products(types)
    points = []
    for i, (item, tr) in enumerate(rows):
        nom = tr.get("designationProduit", "")
        desc = tr.get("descriptifProduit", "")
        slogan = tr.get("slogan", "")
        texte = f"Type: {item.get('typeProduit')} | Nom: {nom} | Description: {desc} | Slogan: {slogan}"
        payload = {
            "ref": item.get("refProduit", ""),
            "type": item.get("typeProduit"),
            "categorie": item.get("categorieLabel", ""),
            "nom": nom,
            "slogan": slogan,
            "description": desc,
            "fournisseur": item.get("fournisseur", ""),
            "prix": item.get("tarifUHTPardefaut", 0),
            "ville": item.get("ville", ""),
            "date": item.get("dateEvent", ""),
        }
        points.append(PointStruct(id=i, vector=embed_passage(texte), payload=payload))

    if points:
        client.upsert(collection_name=collection, points=points)
    return len(points)


# --- Récupération sémantique ---
def retrieve(collection, question, k=3):
    client = get_qdrant()
    res = client.query_points(collection_name=collection, query=embed_query(question), limit=k)
    return [hit.payload for hit in res.points]


def build_context(payloads):
    if not payloads:
        return "(aucun résultat pertinent dans le catalogue)"
    lignes = []
    for p in payloads:
        prix = f"{p.get('prix')} DH" if p.get("prix") else "n/d"
        ville = f" | Ville: {p['ville']}" if p.get("ville") else ""
        date = f" | Date: {p['date']}" if p.get("date") else ""
        fourn = f" par {p['fournisseur']}" if p.get("fournisseur") else ""
        slogan = f" — « {p['slogan']} »" if p.get("slogan") else ""
        lignes.append(
            f"- {p.get('nom')} ({p.get('ref')}){fourn}{slogan} | {p.get('description')} | Prix indicatif: {prix}{ville}{date}"
        )
    return "\n".join(lignes)


# --- Appel LLM (Groq) ---
def ask_llm(system_prompt, user_prompt, temperature=0.6):
    res = get_groq().chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=LLM_MODEL,
        temperature=temperature,
    )
    return res.choices[0].message.content


# --- Pipeline complet d'un agent de domaine : retrieve → contexte → génération ---
def query_domain(collection, question, role_desc):
    payloads = retrieve(collection, question)
    contexte = build_context(payloads)
    system = (
        f"Tu es Yasmine, l'assistante experte {role_desc} de SOS Tourist, le guide touristique du Maroc. "
        "Réponds DANS LA LANGUE du voyageur : français, arabe, anglais, ou darija marocain. "
        "Si la question est en darija, réponds en darija (en lettres latines/arabizi ou arabes selon la question). "
        "Sois chaleureuse, précise et professionnelle, et appuie-toi UNIQUEMENT sur le contexte ci-dessous. "
        "Ne JAMAIS inventer un produit, un prix ou un fournisseur absent du contexte. "
        "Si rien ne correspond, dis-le poliment et propose de reformuler. "
        "En cas d'urgence, rappelle immédiatement le 19 (Police) ou le 15 (Ambulance)."
    )
    user = f"Contexte (catalogue SOS Tourist) :\n{contexte}\n\nQuestion du voyageur : {question}"
    return ask_llm(system, user)


# --- Helpers d'indexation génériques pour les nouvelles sources ---

def _reset_collection(collection):
    client = get_qdrant()
    if client.collection_exists(collection):
        client.delete_collection(collection)
    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )
    return client


def index_produits():
    """Indexe les 605 produits/services réels depuis sos-tourist/DATA."""
    path = os.path.join(_DATA, "produit-service", "produitService.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    client = _reset_collection("produits")
    points = []
    for i, item in enumerate(data):
        tr = next((t for t in item.get("translations", []) if t.get("language") == "fr"), None)
        if not tr:
            continue
        nom = tr.get("designationProduit", "")
        desc = tr.get("descriptifProduit", "")
        slogan = tr.get("slogan", "")
        tags = " ".join(tr.get("tags", []))
        texte = f"Produit: {nom} | {slogan} | {desc} | tags: {tags}"
        payload = {
            "ref": item.get("refProduit", ""),
            "nom": nom,
            "slogan": slogan,
            "description": desc,
            "tags": tags,
            "prix": item.get("tarifUHTPardefaut", 0),
            "ville": item.get("ville", ""),
        }
        points.append(PointStruct(id=i, vector=embed_passage(texte), payload=payload))

    if points:
        client.upsert(collection_name="produits", points=points)
    return len(points)


def index_faq():
    """Indexe les 106 FAQ multilingues."""
    path = os.path.join(_DATA, "faq", "questionsFAQ.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    client = _reset_collection("faq")
    points = []
    i = 0
    for item in data:
        for tr in item.get("translations", []):
            q = tr.get("question", "")
            r = tr.get("reponse", "")
            if not q:
                continue
            texte = f"Question: {q} | Réponse: {r}"
            payload = {
                "ref": item.get("reference", ""),
                "langue": tr.get("language", "fr"),
                "question": q,
                "reponse": r,
            }
            points.append(PointStruct(id=i, vector=embed_passage(texte), payload=payload))
            i += 1

    if points:
        client.upsert(collection_name="faq", points=points)
    return len(points)


def index_acteurs():
    """Indexe les 208 acteurs professionnels (fournisseurs, agences, guides)."""
    path = os.path.join(_DATA, "acteur-pro", "acteursPro.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    client = _reset_collection("acteurs")
    points = []
    for i, item in enumerate(data):
        tr = next((t for t in item.get("translations", []) if t.get("language") == "fr"), None)
        if not tr:
            continue
        nom = tr.get("nomStructure", "")
        desc = tr.get("descriptionActeur", "")
        slogan = tr.get("slogan", "")
        texte = f"Acteur: {nom} | {slogan} | {desc}"
        payload = {
            "ref": item.get("refActorSocioEco", ""),
            "nom": nom,
            "slogan": slogan,
            "description": desc,
            "ville": item.get("ville", ""),
            "contact": item.get("contact", ""),
        }
        points.append(PointStruct(id=i, vector=embed_passage(texte), payload=payload))

    if points:
        client.upsert(collection_name="acteurs", points=points)
    return len(points)


def index_events():
    """Indexe les 302 événements de l'agenda."""
    path = os.path.join(_DATA, "event", "agendaEvent.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    client = _reset_collection("events")
    points = []
    for i, item in enumerate(data):
        tr = next((t for t in item.get("translations", []) if t.get("language") == "fr"), None)
        if not tr:
            continue
        titre = tr.get("designation", "")
        desc = tr.get("description", "")
        texte = f"Événement: {titre} | {desc} | Ville: {item.get('ville', '')} | Date: {item.get('dateDebut', '')}"
        payload = {
            "ref": item.get("refEvent", ""),
            "titre": titre,
            "description": desc,
            "ville": item.get("ville", ""),
            "date_debut": item.get("dateDebut", ""),
            "date_fin": item.get("dateFin", ""),
        }
        points.append(PointStruct(id=i, vector=embed_passage(texte), payload=payload))

    if points:
        client.upsert(collection_name="events", points=points)
    return len(points)


def retrieve_faq(question, k=3):
    """Récupère les FAQ les plus pertinentes dans la langue détectée si possible."""
    client = get_qdrant()
    res = client.query_points(collection_name="faq", query=embed_query(question), limit=k)
    return [hit.payload for hit in res.points]


def build_faq_context(payloads):
    if not payloads:
        return "(aucune FAQ correspondante trouvée)"
    return "\n".join(
        f"Q: {p.get('question')}\nR: {p.get('reponse')}" for p in payloads
    )


def build_acteurs_context(payloads):
    if not payloads:
        return "(aucun prestataire trouvé)"
    return "\n".join(
        f"- {p.get('nom')} — {p.get('slogan')} | {p.get('description')}"
        + (f" | Ville: {p['ville']}" if p.get("ville") else "")
        for p in payloads
    )


def build_events_context(payloads):
    if not payloads:
        return "(aucun événement trouvé)"
    return "\n".join(
        f"- {p.get('titre')} | {p.get('description')}"
        + (f" | {p['ville']}" if p.get("ville") else "")
        + (f" | Début: {p['date_debut']}" if p.get("date_debut") else "")
        for p in payloads
    )
