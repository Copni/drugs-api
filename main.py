"""
FastAPI REST API (single-file) — API privée par clé (X-API-Key)
Fichier: fastapi_drugs_api.py
Instructions de déploiement et README inclus en bas.

Usage locale:
  pip install -r requirements.txt
  export API_KEY="ma_clef_privee"
  uvicorn fastapi_drugs_api:app --host 0.0.0.0 --port 8000

Endpoints protégés par l'entête HTTP `X-API-Key` :
  GET /drugs         -> liste filtrable (params: limit, offset, type, search, min_danger, max_danger, sort_by)
  GET /drugs/{id}    -> détail d'une drogue

Le swagger UI (/docs) et /openapi.json sont également protégés par la clé.
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Any
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED
import uvicorn

API_KEY = os.getenv("API_KEY", "changeme")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")  # pour CORS si besoin

app = FastAPI(title="Drugs Info API (private)")

# --- Data models
class Drug(BaseModel):
    id: int
    nom: str
    type: str
    molecule: str
    risque: str
    effet: str
    prix: Optional[str]
    dangerosite: Optional[int]
    addictif: Optional[int]

# --- In-memory data (données fournies par l'étudiant)
DRUGS: List[dict] = [
    {
        "id": 1,
        "nom": "Cannabis",
        "type": "Drogue psychotrope / stupéfiant (plante dérivée du chanvre)",
        "molecule": "Principalement THC (Δ⁹-tétrahydrocannabinol) ; CBD (cannabidiol) comme composant non psychotrope dans certaines formes",
        "risque": "Troubles cognitifs (mémoire, attention), troubles psychiatriques (dépression, psychose), dépendance psychique, risques pulmonaires liés à la combustion, effets sur le développement cérébral chez les jeunes, risques liés aux produits coupés/toxiques.",
        "effet": "Euphorie, altération de la perception, relaxation ou anxiété selon dose, désinhibition, somnolence, modification de l’humeur et de la cognition.",
        "prix": "≈ 10 €/g pour l’herbe ; ≈ 8 €/g pour la résine (estimation) — selon marché local.",
        "dangerosite": 4,
        "addictif": 3
    },
    {
        "id": 2,
        "nom": "Cocaïne",
        "type": "Psychoactif stimulant (stupéfiant illicite)",
        "molecule": "Chlorhydrate de cocaïne (poudre) ; Crack = forme “free-base” dérivée (bicarbonate/ammoniac) pour fumer",
        "risque": "Risques cardiovasculaires (AVC, infarctus), neurologiques (convulsions), complications pulmonaires (crack), lésions nasales (sniff), infections (usage injectable), troubles psychiatriques (paranoïa, hallucinations).",
        "effet": "Stimulation du SNC (augmentation dopamine, sérotonine, adrénaline) : euphorie, hyperactivité, désinhibition ; effet très rapide pour le crack, courte durée.",
        "prix": "≈ 66 €/g pour la poudre ; crack vendu souvent en galettes de 3–5 consommations ≈ 10-20 € (estimation).",
        "dangerosite": 5,
        "addictif": 4
    },
    {
        "id": 3,
        "nom": "Héroïne",
        "type": "Opioïde / stupéfiant",
        "molecule": "Diacétylmorphine (héroïne) ; dérivés d’opiacés (morphine, codéine, etc.)",
        "risque": "Dépression respiratoire (risque de surdose), dépendance physique et psychique, constipations, infections (usage injectable), risques de contamination (VIH, VHC, VHB), tolérance et sevrage sévère.",
        "effet": "Euphorie, sédation, sensations de calme profond, apaisement, retrait de la douleur, somnolence.",
        "prix": "≈ 28 €/g pour héroïne (prix de détail courant) en France.",
        "dangerosite": 5,
        "addictif": 5
    },
    {
        "id": 4,
        "nom": "MDMA",
        "type": "Entactogène / stimulant empathogène",
        "molecule": "3,4-méthylènedioxyméthamphétamine (MDMA)",
        "risque": "Hyperthermie, déshydratation, déséquilibre électrolytique, crises cardiaques, convulsions, troubles psychiatriques (anxiété, dépression), risques de neurotoxicité, confusion/malaises.",
        "effet": "Empathie accrue, sociabilité, éveil sensoriel, euphorie, stimulation, augmentation de l’énergie et de l’empathie.",
        "prix": "Varie selon pays ; typiquement comprimés de 5-10€ ou plus selon pureté / marché local (estimation).",
        "dangerosite": 4,
        "addictif": 3
    },
    {
        "id": 5,
        "nom": "Amphétamines",
        "type": "Stimulant / amphétaminique",
        "molecule": "Amphétamine (ou dérivés comme méthamphetamine, etc.)",
        "risque": "Agitation, insomnie, hypertension, tachycardie, infarctus, psychose, troubles neurologiques, surchauffe, dépendance psychique/factice.",
        "effet": "Stimulation, éveil, augmentation de l’énergie, réduction de la fatigue, vigilance accrue, augmentation du rythme cardiaque.",
        "prix": "Variable selon marché local ; estimation souvent similaire ou inférieure à la cocaïne selon pureté.",
        "dangerosite": 4,
        "addictif": 4
    },
    {
        "id": 6,
        "nom": "LSD",
        "type": "Hallucinogène / psychédélique",
        "molecule": "Acide lysergique diéthylamide (LSD)",
        "risque": "Bad trips, psychose aiguë, paranoïa, flashbacks, risque psychologique chez personnes vulnérables, hypertension, agitation.",
        "effet": "Altération de la perception (visuelle, auditive), distorsion temporelle, hallucinations, introspection, expériences mystiques possibles.",
        "prix": "Généralement vendu sous forme de “lits” ou “blotters” de 5 à 20 € selon le pays (estimation).",
        "dangerosite": 3,
        "addictif": 1
    },
    {
        "id": 7,
        "nom": "Kétamine",
        "type": "Dissociatif / anesthésique détourné",
        "molecule": "Kétamine (R/S racémique) ; dérivés comme la kétamine chirurgicale",
        "risque": "Troubles urinaires (cystite), dommages rénaux, hallucinations, confusion, dépendance psychique, overdose possible surtout en combinaison, effets dissociatifs dangereux.",
        "effet": "Dissociation, anesthésie partielle (hors usage médical), altération sensorielle, dépersonnalisation, hallucinations.",
        "prix": "Varie selon marché ; estimation dépend du pays, de la pureté.",
        "dangerosite": 4,
        "addictif": 3
    },
    {
        "id": 8,
        "nom": "Benzodiazépines",
        "type": "Sédatif / anxiolytique (médicaments détournés)",
        "molecule": "Diazépam, alprazolam, lorazépam, etc. (dérivés benzodiazépinés)",
        "risque": "Somnolence, confusion, dépression respiratoire en combinaison, tolérance, dépendance physique, sevrage sévère (convulsions), surdosage si mélange alcool ou opioïdes.",
        "effet": "Anxiolyse, sédation, relaxation musculaire, somnolence, amnésie partielle.",
        "prix": "En usage illicite, prix de marché noir varie, souvent inférieur à celui des drogues “classiques”.",
        "dangerosite": 3,
        "addictif": 4
    },
    {
        "id": 9,
        "nom": "Méthamphétamine",
        "type": "Stimulant puissant / amphétaminique",
        "molecule": "Méthamphétamine (crystal meth, variante de l’amphétamine)",
        "risque": "Psychose, surchauffe, cardiovasculaire sévères, neurologiques, perte de poids extrême, comportement compulsif, dommages dentaires sévères (”meth mouth”).",
        "effet": "Stimulation intense, éveil extrême, euphorie, hyperactivité, réduction drastique de l’appétit, perte de fatigue.",
        "prix": "Varie fortement selon le marché local ; estimation plus élevé dans certains endroits à cause de pureté/cristal.",
        "dangerosite": 5,
        "addictif": 5
    },
    {
        "id": 10,
        "nom": "NPS",
        "type": "Substances psychoactives de synthèse (designer drugs, analogues) non encore réglementées",
        "molecule": "Très variable : cannabinoïdes de synthèse, cathinones de synthèse, opioïdes de synthèse, phénéthylamines de synthèse, etc.",
        "risque": "Grande variabilité, surdosage, effets imprévisibles, décès signalés, intoxications aiguës, confusion, convulsions, risques neurologiques / cardiovasculaires, dépendance possible.",
        "effet": "Selon la molécule : stimulants (comme MDMA, amphétamines), hallucinogènes, dépresseurs etc., imitation d’effets de drogues classiques mais avec puissance / risques incertains.",
        "prix": "Souvent entre 8 et 20 €/g en ligne pour certains NPS (estimation).",
        "dangerosite": 5,
        "addictif": 4
    }
]

# --- Security: middleware to protect all paths (including docs)
class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow healthcheck if you want (uncomment below)
        # if request.url.path == "/health":
        #     return await call_next(request)
        key = request.headers.get("X-API-Key")
        if not key or key != API_KEY:
            return JSONResponse({"detail": "Unauthorized"}, status_code=HTTP_401_UNAUTHORIZED)
        return await call_next(request)

# Attach middleware only if API_KEY is set to something non-empty
if API_KEY:
    app.add_middleware(APIKeyMiddleware)

# --- Helper functions

def find_drug(did: int) -> Optional[dict]:
    for d in DRUGS:
        if d["id"] == did:
            return d
    return None

# --- Routes
@app.get("/drugs", response_model=List[Drug])
async def list_drugs(
    limit: int = 10,
    offset: int = 0,
    type: Optional[str] = None,
    search: Optional[str] = None,
    min_danger: Optional[int] = None,
    max_danger: Optional[int] = None,
    sort_by: Optional[str] = None,
):
    """Retourne une liste filtrée de drogues en mémoire.

    Paramètres utiles:
    - limit: nombre maximal d'éléments retournés
    - offset: décalage pour pagination
    - type: filtre sur le champ `type` (contain, insensible à la casse)
    - search: recherche texte sur `nom` et `molecule`
    - min_danger / max_danger: filtre sur `dangerosite`
    - sort_by: champ pour trier ("dangerosite", "addictif", "nom"). Préfixez '-' pour desc.
    """
    results = DRUGS.copy()

    # filter by type substring
    if type:
        q = type.lower()
        results = [r for r in results if q in (r.get("type") or "").lower()]

    # search in nom or molecule
    if search:
        q = search.lower()
        results = [r for r in results if q in (r.get("nom") or "").lower() or q in (r.get("molecule") or "").lower()]

    # danger filters
    if min_danger is not None:
        results = [r for r in results if (r.get("dangerosite") is not None and r.get("dangerosite") >= min_danger)]
    if max_danger is not None:
        results = [r for r in results if (r.get("dangerosite") is not None and r.get("dangerosite") <= max_danger)]

    # sort
    if sort_by:
        reverse = False
        key = sort_by
        if sort_by.startswith("-"):
            reverse = True
            key = sort_by[1:]
        results = sorted(results, key=lambda x: (x.get(key) is None, x.get(key)), reverse=reverse)

    # pagination
    paginated = results[offset: offset + limit]
    return paginated


@app.get("/drugs/{drug_id}", response_model=Drug)
async def get_drug(drug_id: int):
    d = find_drug(drug_id)
    if not d:
        raise HTTPException(status_code=404, detail="Drug not found")
    return d


# Optional healthcheck (si vous souhaitez exposer une route non protégée, il faudrait l'exclure du middleware)
@app.get("/health")
async def health():
    return {"status": "ok"}


# --- If run directly
if __name__ == "__main__":
    uvicorn.run("fastapi_drugs_api:app", host="0.0.0.0", port=8000, reload=True)


# -----------------------------
# README / Déploiement (README rapide)
# -----------------------------
# Requirements (requirements.txt) :
# fastapi
# uvicorn[standard]
# python-dotenv  # optionnel
#
# Déploiement - notes rapides :
# - Vercel : Vercel supporte les projets Python via le builder "vercel-python" ou en utilisant un Dockerfile. Pour une API FastAPI privée,
#   définissez la variable d'environnement API_KEY dans le dashboard Vercel et déployez le projet. Protégez toujours la clé et évitez de
#   l'inclure dans le code.
# - Autres services simples : Render, Railway, Fly, Google Cloud Run. Tous permettent d'ajouter des variables d'environnement.
#
# Exemple (Dockerfile minimal) :
#   FROM python:3.11-slim
#   WORKDIR /app
#   COPY . /app
#   RUN pip install --no-cache-dir fastapi uvicorn[standard]
#   ENV API_KEY=changeme
#   CMD ["uvicorn", "fastapi_drugs_api:app", "--host", "0.0.0.0", "--port", "$PORT"]
#
# Sécurité :
# - Ne laissez pas la clé API par défaut (changeme) en production.
# - Pour un usage étudiant interne, cette protection est suffisante. Pour une vraie prod, combinez HTTPS + authentification utilisateur + audit.
#
# Extensions possibles (si tu veux que je les ajoute) :
# - POST /drugs pour ajouter (protégé)
# - PUT/PATCH/DELETE pour modifier
# - Tests unitaires + Dockerfile + workflow GitHub Actions
# - Pagination complète et métadonnées (total, page)
#
# Fin du fichier.
