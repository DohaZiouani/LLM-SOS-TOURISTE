"""Génère produitService_dataset.json au format MongoDB-like (mêmes champs que SOS Tourist),
à partir du catalogue réel extrait du cahier des charges / prototype."""
import json

# (ref, typeProduit, categorieLabel, nom, slogan, fournisseur, prixHT, ville, descriptif)
PRODUITS = [
    ("PROD-2024-005", "Riad", "Hébergement", "Nuit Suite Royale Riad", "Le luxe d'Orient",
     "Riad Dar Salam", 1450, "Marrakech",
     "Suite royale au cœur de la médina de Marrakech : décor d'Orient raffiné, piscine intérieure, terrasse et petit-déjeuner marocain. Idéal pour un séjour de luxe au calme."),
    ("PROD-2024-007", "Hotel", "Hébergement", "Chambre Double Vue Mer", "Réveillez-vous face à l'océan",
     "Surf Camp Taghazout", 780, "Taghazout",
     "Chambre double avec balcon et vue directe sur l'Atlantique, à deux pas des spots de surf de Taghazout. Parfait pour allier détente et glisse."),
    ("PROD-2024-012", "Restaurant", "Restauration", "Dîner Gastronomique Dar Moha", "7 services revisitant la tradition",
     "Restaurant Dar Moha", 520, "Marrakech",
     "Menu dégustation en 7 services de cuisine marocaine revisitée par le chef, servi dans un cadre raffiné de la médina. Tajines, pastilla et créations contemporaines."),
    ("PROD-2024-003", "Artisanat", "Artisanat", "Huile d'Argan Bio 100ml", "L'élixir de beauté pur",
     "Coopérative Argania", 120, "Agadir",
     "Huile d'argan biologique 100 % pure, pressée à froid par une coopérative féminine du Souss. Cosmétique authentique, packaging soigné, certifiée bio."),
    ("PROD-2024-014", "Artisanat", "Artisanat", "Coffret Argan Découverte", "Trois huiles, une coopérative",
     "Coopérative Argania", 240, "Agadir",
     "Coffret cadeau réunissant trois huiles d'argan (cosmétique, alimentaire, parfumée) issues d'une coopérative berbère. Idéal en souvenir ou en cadeau."),
    ("PROD-2024-004", "Activitie", "Trek", "Trek Atlas 3 Jours", "Au sommet de l'aventure",
     "Azur Expeditions", 350, "Imlil",
     "Trek de 3 jours dans le Haut-Atlas avec guide certifié : villages berbères, cols panoramiques et nuit en gîte. Randonnée éco-responsable, niveau intermédiaire."),
    ("PROD-2024-006", "Activitie", "Trek", "Trek Atlas Groupe Privé", "Une aventure sur mesure dans le Haut-Atlas",
     "Azur Expeditions", 500, "Imlil",
     "Trek privatisé et personnalisable dans le Haut-Atlas pour groupes : itinéraire sur mesure, rythme adapté, guide dédié. Tarif dégressif selon le nombre de participants."),
    ("PROD-2024-015", "Activitie", "Trek", "Ascension Toubkal 2 Jours", "4167 m — au sommet de l'Afrique du Nord",
     "Guide Brahim Ait Ouahmane", 1200, "Imlil",
     "Ascension du Toubkal (4167 m), plus haut sommet d'Afrique du Nord, en 2 jours avec guide de montagne certifié. Refuge, lever de soleil au sommet, encadrement sécurisé."),
    ("PROD-2024-010", "Activitie", "Aventure", "Bivouac Étoilé Merzouga", "Une nuit sous le ciel du Sahara",
     "Sahara Bivouac Merzouga", 680, "Merzouga",
     "Nuit en bivouac dans les dunes de Merzouga : balade à dos de dromadaire, feu de camp, dîner berbère et ciel étoilé du Sahara. Expérience inoubliable du désert."),
    ("PROD-2024-011", "Activitie", "Aventure", "Initiation Surf Taghazout", "Vos premières vagues atlantiques",
     "Surf Camp Taghazout", 280, "Taghazout",
     "Session d'initiation au surf sur la côte atlantique de Taghazout : matériel fourni, moniteur diplômé, spots adaptés aux débutants. Convient à tous les niveaux."),
    ("PROD-2024-013", "Activitie", "Visite", "Visite Médina Chefchaouen", "La perle bleue, sans foule",
     "Eco-Tours Chefchaouen", 180, "Chefchaouen",
     "Visite guidée à pied de la médina bleue de Chefchaouen, loin des foules : ruelles, artisanat local, points de vue photo. Tourisme durable et authentique."),
    ("PROD-2024-016", "Activitie", "Atelier", "Atelier Cuisine Marocaine", "De la médina à votre tagine",
     "Restaurant Dar Moha", 380, "Marrakech",
     "Atelier de cuisine marocaine : marché aux épices, préparation d'un tajine et d'une pastilla avec un chef, puis dégustation. Repartez avec les recettes traditionnelles."),
]

# (ref, titre, ville, date, desc)
EVENEMENTS = [
    ("EV-2024-MAR-01", "Festival des Gnaouas", "Essaouira", "22 Juin",
     "Célébration annuelle de la musique et de la culture gnaouie d'Essaouira : concerts, fusion et patrimoine immatériel."),
    ("EV-2024-ATL-05", "Trek de la Solidarité", "Imlil", "08 Juillet",
     "Trek communautaire dans le Haut-Atlas au profit des écoles de montagne. Randonnée solidaire ouverte à tous."),
    ("EV-2024-MEK-02", "Atelier Argan & Femmes", "Tafraoute", "15 Septembre",
     "Rencontre avec les coopératives berbères et démonstration de pressage à froid de l'huile d'argan."),
]

data = []
oid = 1
for ref, tp, cat, nom, slogan, fourn, prix, ville, desc in PRODUITS:
    data.append({
        "_id": {"$oid": f"{oid:024d}"},
        "refProduit": ref,
        "typeProduit": tp,
        "categorieLabel": cat,
        "fournisseur": fourn,
        "ville": ville,
        "tarifUHTPardefaut": prix,
        "imageProduit": "",
        "etatDePublication": "code_3417",
        "translations": [
            {"language": "fr", "designationProduit": nom, "slogan": slogan, "descriptifProduit": desc},
        ],
    })
    oid += 1

for ref, titre, ville, date, desc in EVENEMENTS:
    data.append({
        "_id": {"$oid": f"{oid:024d}"},
        "refProduit": ref,
        "typeProduit": "Event",
        "categorieLabel": "Événement",
        "fournisseur": "",
        "ville": ville,
        "dateEvent": date,
        "tarifUHTPardefaut": 0,
        "imageProduit": "",
        "etatDePublication": "code_3417",
        "translations": [
            {"language": "fr", "designationProduit": titre, "slogan": "", "descriptifProduit": desc},
        ],
    })
    oid += 1

with open("produitService_dataset.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"{len(data)} éléments écrits ({len(PRODUITS)} produits + {len(EVENEMENTS)} événements)")
