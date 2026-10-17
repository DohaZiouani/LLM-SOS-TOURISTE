import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_rag import query_domain

COLLECTION = "activites"
ROLE = "en activités, treks, excursions et événements"

def interroger_agent_activites(question):
    return query_domain(COLLECTION, question, ROLE)

if __name__ == "__main__":
    print(interroger_agent_activites("Je veux faire un trek dans l'Atlas, quelles options ?"))
