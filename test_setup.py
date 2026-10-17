"""Vérifie que les 3 briques fonctionnent : Groq, Qdrant (local), embeddings."""
import os
from dotenv import load_dotenv
load_dotenv()

print("1/3 — Test Groq…")
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
resp = client.chat.completions.create(
    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    messages=[
        {"role": "system", "content": "Tu es Yasmine, l'assistante de SOS Tourist. Sois chaleureuse et accueillante."},
        {"role": "user", "content": "Dis bonjour et souhaite la bienvenue au Maroc."},
    ],
)
print("   ✅ Groq OK :", resp.choices[0].message.content[:120], "…")

print("2/3 — Test Qdrant (local)…")
from qdrant_client import QdrantClient
qdrant = QdrantClient(path=os.getenv("QDRANT_PATH", "./qdrant_data"))
print("   ✅ Qdrant OK :", [c.name for c in qdrant.get_collections().collections])

print("3/3 — Test embeddings (e5-large)…")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer(os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-large"))
vec = model.encode("query: test SOS Tourist")
print("   ✅ Embeddings OK : dimension =", len(vec))

print("\n🎉 Setup complet — tu peux lancer l'indexation (python indexing/index_all.py).")
