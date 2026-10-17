import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_rag import retrieve, build_acteurs_context, ask_llm


def interroger_agent_acteurs(question):
    payloads = retrieve("acteurs", question, k=4)
    contexte = build_acteurs_context(payloads)
    system = (
        "Tu es Yasmine, l'assistante de SOS Tourist. "
        "Réponds DANS LA LANGUE du voyageur (français, arabe, anglais ou darija). "
        "Présente les prestataires/agences/guides du catalogue ci-dessous de façon chaleureuse. "
        "Ne cite que des acteurs présents dans le contexte. "
        "En cas d'urgence, rappelle le 19 ou le 15."
    )
    user = f"Prestataires SOS Tourist :\n{contexte}\n\nQuestion : {question}"
    return ask_llm(system, user)
