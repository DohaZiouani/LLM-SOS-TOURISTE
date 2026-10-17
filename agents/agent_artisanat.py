import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_rag import query_domain

COLLECTION = "artisanat"
ROLE = "en artisanat marocain et produits de coopératives"

def interroger_agent_artisanat(question):
    return query_domain(COLLECTION, question, ROLE)

if __name__ == "__main__":
    print(interroger_agent_artisanat("Je cherche de l'huile d'argan authentique en cadeau"))
