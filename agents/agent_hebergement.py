import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_rag import query_domain

COLLECTION = "hebergement"
ROLE = "en hébergement (riads, hôtels, maisons d'hôtes)"

def interroger_agent_hebergement(question):
    return query_domain(COLLECTION, question, ROLE)

if __name__ == "__main__":
    print(interroger_agent_hebergement("Je cherche un riad de charme avec piscine à Marrakech"))
