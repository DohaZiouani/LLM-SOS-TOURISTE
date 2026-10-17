"""
orchestrateur.py — le « LLM Global » de SOS Tourist.

Routage en 2 temps :
  1. routeur par mots-clés (gratuit, instantané)
  2. si ambigu → routeur par LLM (Groq classe la question en un mot)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_rag import ask_llm
from agents.agent_hebergement import interroger_agent_hebergement
from agents.agent_restauration import interroger_agent_restauration
from agents.agent_activites import interroger_agent_activites
from agents.agent_artisanat import interroger_agent_artisanat
from agents.agent_faq import interroger_agent_faq
from agents.agent_acteurs import interroger_agent_acteurs
from agents.agent_events import interroger_agent_events

AGENTS = {
    "hebergement": interroger_agent_hebergement,
    "restauration": interroger_agent_restauration,
    "activites": interroger_agent_activites,
    "artisanat": interroger_agent_artisanat,
    "faq": interroger_agent_faq,
    "acteurs": interroger_agent_acteurs,
    "events": interroger_agent_events,
}

MOTS_CLES = {
    "hebergement": ["riad", "hôtel", "hotel", "chambre", "dormir", "nuit", "héberg", "loger", "gîte", "suite", "airbnb"],
    "restauration": ["restaurant", "manger", "dîner", "diner", "gastronom", "repas", "tajine", "table", "couvert", "café", "couscous"],
    "activites": ["trek", "randonn", "surf", "activité", "visite", "excursion", "bivouac", "désert", "dune",
                  "atelier", "montagne", "toubkal", "atlas", "ascension", "quad", "hammam", "spa"],
    "artisanat": ["argan", "artisan", "coopérative", "cooperative", "souvenir", "huile", "cosmét", "cadeau", "coffret", "poterie", "zellige"],
    "faq": ["urgence", "passeport", "visa", "sécurité", "police", "ambulance", "blessé", "volé", "perdu",
            "comment", "puis-je", "est-ce que", "faut-il", "doit-on", "horaire", "prix", "tarif"],
    "acteurs": ["agence", "guide", "prestataire", "opérateur", "société", "entreprise", "contact", "réserver auprès"],
    "events": ["festival", "événement", "evenement", "agenda", "concert", "fête", "célébration", "programme", "sortie"],
}

DOMAINE_DEFAUT = "faq"


def router_par_mots(question):
    q = question.lower()
    scores = {dom: sum(1 for m in mots if m in q) for dom, mots in MOTS_CLES.items()}
    meilleur = max(scores, key=scores.get)
    return meilleur if scores[meilleur] > 0 else None


def router_par_llm(question):
    consigne = (
        "Tu es un routeur. Classe la question du voyageur dans UNE seule catégorie parmi : "
        "hebergement, restauration, activites, artisanat, faq, acteurs, events. "
        "Réponds par un seul mot, rien d'autre."
    )
    rep = ask_llm(consigne, question, temperature=0).strip().lower()
    for dom in AGENTS:
        if dom in rep:
            return dom
    return None


def repondre(question, routeur_llm=True, verbose=True):
    domaine = router_par_mots(question)
    if domaine is None and routeur_llm:
        domaine = router_par_llm(question)
    if domaine is None:
        domaine = DOMAINE_DEFAUT
    if verbose:
        print(f"[Orchestrateur] question orientée vers l'agent « {domaine} »")
    return AGENTS[domaine](question)


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Que faire si je perds mon passeport au Maroc ?"
    print("\n--- Réponse Yasmine ---")
    print(repondre(question))
