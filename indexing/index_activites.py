import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_rag import index_domain

COLLECTION = "activites"
TYPES = ["Activitie", "Event"]   # treks, surf, bivouac, visites, ateliers + événements

if __name__ == "__main__":
    n = index_domain(COLLECTION, TYPES)
    print(f"✅ Indexation « {COLLECTION} » : {n} activités/événements ajoutés.")
