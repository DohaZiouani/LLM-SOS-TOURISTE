import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_rag import index_domain, index_produits, index_faq, index_acteurs, index_events

DOMAINES = {
    "hebergement": ["Hotel", "Riad", "Gite"],
    "restauration": ["Restaurant"],
    "activites": ["Activitie", "Event"],
    "artisanat": ["Artisanat"],
}

if __name__ == "__main__":
    total = 0

    print("\n── Indexation des domaines (dataset legacy) ──")
    for collection, types in DOMAINES.items():
        n = index_domain(collection, types)
        total += n
        print(f"  • {collection:<13} : {n} éléments")

    print("\n── Indexation des sources réelles ──")
    n = index_produits()
    total += n
    print(f"  • produits       : {n} produits/services")

    n = index_faq()
    total += n
    print(f"  • faq            : {n} entrées FAQ (toutes langues)")

    n = index_acteurs()
    total += n
    print(f"  • acteurs        : {n} acteurs professionnels")

    n = index_events()
    total += n
    print(f"  • events         : {n} événements agenda")

    print(f"\n✅ Indexation terminée — {total} éléments au total dans Qdrant.")
