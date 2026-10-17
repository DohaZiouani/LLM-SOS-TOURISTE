import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_rag import retrieve, build_events_context, ask_llm


def interroger_agent_events(question):
    payloads = retrieve("events", question, k=4)
    contexte = build_events_context(payloads)
    system = (
        "Tu es Yasmine, l'assistante de SOS Tourist. "
        "Réponds DANS LA LANGUE du voyageur (français, arabe, anglais ou darija). "
        "Présente les événements de l'agenda SOS Tourist de façon enthousiaste et précise. "
        "Ne mentionne que des événements présents dans le contexte ci-dessous."
    )
    user = f"Agenda SOS Tourist :\n{contexte}\n\nQuestion : {question}"
    return ask_llm(system, user)
