# Feuille de route — Finir mon LLM SOS Tourist (du début à la fin)

Tu as **3 morceaux** :
- **App MEAN + widget Yasmine + route `/api/chat`** → package `yasmine-integration`
- **Service RAG Python** (le « cerveau ») → package `sos-tourist-LLM` (celui-ci)
- **Le CDC** → la vision complète (fine-tuning LLaMA, Edge AI…) = recherche, plus tard

**Objectif réaliste « fini » =** un assistant RAG qui marche de bout en bout :
widget Yasmine → Express → RAG Python → réponse **ancrée sur tes 607 produits**.
Le fine-tuning LLaMA du CDC est une **phase séparée** (voir Phase 5) — ton RAG est
déjà un livrable complet et démontrable.

---

## PHASE 0 — Pré-requis (sur ton serveur Linux)
- Python 3.10+ et Node 18+ (`python3 --version`, `node -v`)
- Ton app MEAN qui démarre déjà
- MongoDB accessible
- Une **clé Groq gratuite** → https://console.groq.com → API Keys

---

## PHASE 1 — Faire tourner le RAG en local (données de démo)

```bash
# 1. transférer sos-tourist-LLM.zip sur le serveur (WinSCP/scp), puis :
unzip sos-tourist-LLM.zip && cd sos-tourist-LLM

# 2. environnement Python isolé
python3 -m venv venv && source venv/bin/activate

# 3. dépendances
pip install -r requirements.txt

# 4. clé API
cp .env.example .env
nano .env            # mets GROQ_API_KEY=gsk_...

# 5. vérifier les 3 briques (⚠️ télécharge e5-large ~2 Go la 1re fois)
python test_setup.py

# 6. indexer les données de démo (15 éléments)
python indexing/index_all.py

# 7. parler à Yasmine
python chat_cli.py
```
✅ **Si Yasmine répond, ton RAG fonctionne.**

---

## PHASE 2 — Brancher TES vraies données (607 produits)

```bash
# 8. exporter ta collection MongoDB en JSON
mongoexport --uri="mongodb://...ta_base" \
  --collection=produitService \
  --jsonArray --out=produitService_dataset.json
```

**9. Vérifier que chaque produit a bien :**
- `typeProduit` valant un de : `Hotel`, `Riad`, `Gite`, `Restaurant`, `Activitie`, `Artisanat`, `Event`
- `translations[]` avec une entrée `{ "language": "fr", "designationProduit", "slogan", "descriptifProduit" }`
- `refProduit`, `tarifUHTPardefaut`, `ville`

> Si ta base n'a **pas** de champ `typeProduit`, dérive-le de ta catégorie/taxonomie
> avec un petit script (ou adapte `load_products()` dans `core_rag.py` pour filtrer
> sur ton vrai champ). Les domaines/types se règlent dans `indexing/index_*.py`.

```bash
# 10. remplacer le dataset de démo par ton export
mv produitService_dataset.json sos-tourist-LLM/produitService_dataset.json
#    (ou, sans déplacer : mettre DATASET_PATH=/chemin/export.json dans .env)

# 11. ré-indexer tout ton catalogue
python indexing/index_all.py
```
✅ **Le RAG connaît maintenant tout ton catalogue** (il retrouve les bons parmi 607).

---

## PHASE 3 — Exposer en API + brancher sur Yasmine / Express

```bash
# 12. lancer le service RAG (laisse-le tourner)
uvicorn api:app --host 0.0.0.0 --port 8001
#     test rapide :
curl -X POST http://localhost:8001/chat -H "Content-Type: application/json" \
     -d '{"question":"un trek dans l_Atlas ?"}'
```

**13. Côté Node (ton app MEAN) :**
```bash
cp express-bridge/chat.rag.js  TON_PROJET/routes/
```
Dans `server.js`, monte la version RAG (à la place de l'ancienne) :
```js
app.use(express.json({ limit: '1mb' }));
app.use('/api/chat', require('./routes/chat.rag'));   // ← remplace ./routes/chat
```
Dans le `.env` Node :
```
RAG_URL=http://localhost:8001/chat
```

```bash
# 14. démarrer Node + Angular
node server.js
ng serve --proxy-config proxy.conf.json
```
Ouvre le widget Yasmine → pose une question → **réponse RAG ancrée sur tes données.**
✅ **Bout en bout terminé.**

> **Garder le service Python vivant en prod** (pas juste `uvicorn` à la main) :
> `pm2 start "uvicorn api:app --port 8001" --name rag-sos` ou un service `systemd`.

---

## PHASE 4 — Darija (ce que demande le CDC)

**Niveau 1 — déjà fait ✅** : Yasmine répond désormais **dans la langue de la
question** (FR / AR / EN / darija) — le prompt de `core_rag.py` a été adapté. Pose
une question en darija → elle répond en darija.

**Niveau 2 — vraie qualité darija (travail de DONNÉES, pas de code) :**
- Ajoute des traductions **arabe/darija** dans le dataset :
  `translations: [{language:"fr",...}, {language:"ary", designationProduit:"...", descriptifProduit:"..."}]`
  → la récupération devient bonne aussi pour des requêtes en darija.
- (Optionnel, avancé) un **embedding dédié arabe/darija** (le CDC cite
  *Arabic-Matryoshka*) en plus d'e5-large.
- C'est le **WP-2 du CDC** (corpus darija : 150 Mo + 80 h audio) — gros effort de
  collecte, indépendant du code.

---

## PHASE 5 — Aller plus loin (CDC, recherche — optionnel)
- **Fine-tuning LLaMA 3.1** (QLoRA + DPO) sur tes données → remplace Groq/Llama par
  ton modèle.
- **Edge AI offline** (Phi-3 Mini ONNX), **multi-index certifié**, agents BDI…
- = phase recherche séparée. **Pas nécessaire** pour avoir un assistant qui marche.

---

## Récap : les 2 services à faire tourner ensemble
| Terminal | Commande | Rôle |
|---|---|---|
| 1 | `uvicorn api:app --port 8001` | le cerveau RAG (Python) |
| 2 | `node server.js` | l'API MEAN + le pont vers le RAG |
| 3 | `ng serve --proxy-config proxy.conf.json` | le front (widget Yasmine) |

## Pour la démo / soutenance
1. Question en **français** → un vrai produit du catalogue est cité.
2. *« Y a-t-il un trek au Mont Everest ? »* → refus poli + alternative marocaine.
3. Question en **darija** → réponse en darija.
4. Montre l'orchestrateur : `python orchestrateur.py "je veux un riad à Marrakech"`
   → il route vers l'agent `hebergement`.
