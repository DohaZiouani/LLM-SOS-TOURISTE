import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_rag import query_domain

COLLECTION = "restauration"
ROLE = "en restauration et gastronomie marocaine"

def interroger_agent_restauration(question):
    return query_domain(COLLECTION, question, ROLE)

if __name__ == "__main__":
    print(interroger_agent_restauration("Où dîner une bonne cuisine marocaine à Marrakech ?"))
