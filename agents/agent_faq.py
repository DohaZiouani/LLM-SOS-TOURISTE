import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_rag import retrieve_faq, build_faq_context, ask_llm


def interroger_agent_faq(question):
    payloads = retrieve_faq(question, k=4)
    contexte = build_faq_context(payloads)
    system = (
        "Tu es Yasmine, l'assistante officielle de SOS Tourist — guide touristique du Maroc. "
        "Réponds DANS LA LANGUE du voyageur (français, arabe, anglais ou darija). "
        "Appuie-toi sur les FAQ ci-dessous pour donner une réponse précise et rassurante. "
        "En cas d'urgence médicale ou de sécurité, rappelle immédiatement : Police 19, Ambulance 15."
    )
    user = f"FAQ SOS Tourist :\n{contexte}\n\nQuestion : {question}"
    return ask_llm(system, user)
