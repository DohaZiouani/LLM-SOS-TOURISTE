"""Teste les 4 agents experts + l'orchestrateur. (Lance d'abord index_all.py.)"""
from dotenv import load_dotenv
load_dotenv()

from agents.agent_hebergement import interroger_agent_hebergement
from agents.agent_restauration import interroger_agent_restauration
from agents.agent_activites import interroger_agent_activites
from agents.agent_artisanat import interroger_agent_artisanat
from orchestrateur import repondre

print("=" * 64)
print("🤖 SOS TOURIST — TEST DES AGENTS EXPERTS (Yasmine)")
print("=" * 64)

cas = [
    ("🏨 Hébergement", interroger_agent_hebergement, "Un riad de luxe à Marrakech ?"),
    ("🍽️  Restauration", interroger_agent_restauration, "Où bien manger marocain à Marrakech ?"),
    ("🥾 Activités",    interroger_agent_activites,    "Je veux faire un trek dans l'Atlas."),
    ("🧴 Artisanat",    interroger_agent_artisanat,    "De l'huile d'argan authentique en cadeau ?"),
]
for titre, fn, q in cas:
    print(f"\n{titre} — Q: {q}")
    try:
        print("→", fn(q))
    except Exception as e:
        print("❌", e)
    print("-" * 64)

print("\n🧭 Orchestrateur (routage automatique) :")
for q in ["Je cherche une nuit dans le désert de Merzouga",
          "Un cadeau artisanal du Souss ?"]:
    print(f"\nQ: {q}")
    try:
        print("→", repondre(q))
    except Exception as e:
        print("❌", e)

print("\n🎉 Fin des tests.")
