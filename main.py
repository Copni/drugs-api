from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="InfoDrogues API",
    description="API REST pour la prévention contre la drogue (projet étudiant)",
    version="1.1.0"
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en production, restreins ton domaine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Clé d'accès privée ---
API_KEY = "ILoveDrugs"

# --- Données en mémoire ---
substances = [
    {
        "id": 1,
        "nom": "Cannabis (résine, herbe, huile, CBD)",
        "type": "Drogue psychotrope / stupéfiant (plante dérivée du chanvre)",
        "molecule": "THC, CBD",
        "risque": "Troubles cognitifs, dépendance psychique, effets pulmonaires.",
        "effet": "Euphorie, relaxation, altération de la perception.",
        "prix": "≈ 10 €/g",
        "dangerosite": 4,
        "addictif": 3
    },
    {
        "id": 2,
        "nom": "Cocaïne / Crack",
        "type": "Stimulant",
        "molecule": "Chlorhydrate de cocaïne",
        "risque": "Troubles cardiovasculaires, psychose, dépendance élevée.",
        "effet": "Euphorie, hyperactivité, désinhibition.",
        "prix": "≈ 66 €/g",
        "dangerosite": 5,
        "addictif": 4
    },
    {
        "id": 3,
        "nom": "Héroïne / Opiacés",
        "type": "Opioïde / stupéfiant",
        "molecule": "Diacétylmorphine (héroïne)",
        "risque": "Risque de surdose, dépendance physique, infections.",
        "effet": "Euphorie, sédation, somnolence.",
        "prix": "≈ 28 €/g",
        "dangerosite": 5,
        "addictif": 5
    },
    {
        "id": 4,
        "nom": "MDMA / Ecstasy",
        "type": "Stimulant empathogène",
        "molecule": "3,4-méthylènedioxyméthamphétamine (MDMA)",
        "risque": "Hyperthermie, déshydratation, troubles psychiatriques.",
        "effet": "Euphorie, empathie, énergie accrue.",
        "prix": "≈ 10 €/comprimé",
        "dangerosite": 4,
        "addictif": 3
    },
    {
        "id": 5,
        "nom": "LSD",
        "type": "Hallucinogène",
        "molecule": "Acide lysergique diéthylamide (LSD)",
        "risque": "Bad trips, psychose, anxiété aiguë.",
        "effet": "Hallucinations visuelles et auditives, distorsion du temps.",
        "prix": "≈ 10 €/unité",
        "dangerosite": 3,
        "addictif": 1
    },
]

# --- Vérification de la clé API ---
def check_auth(auth: str = Header(None)):
    if auth != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Clé d'accès invalide ou manquante.")


# --- Endpoint : Liste des drogues ---
@app.get("/drugs")
def get_drugs(
    limit: int | None = Query(None, description="Nombre maximum de drogues à renvoyer"),
    type: str | None = Query(None, description="Filtrer par type de drogue"),
    search: str | None = Query(None, description="Rechercher par nom"),
    Authorization: str = Header(None)
):
    check_auth(Authorization)

    results = substances

    # Filtrage par type
    if type:
        results = [d for d in results if type.lower() in d["type"].lower()]

    # Filtrage par recherche
    if search:
        results = [d for d in results if search.lower() in d["nom"].lower()]

    # Limitation du nombre de résultats
    if limit:
        results = results[:limit]

    return results


# --- Endpoint : Détails d'une drogue ---
@app.get("/drugs/{drug_id}")
def get_drug(drug_id: int, Authorization: str = Header(None)):
    check_auth(Authorization)

    for d in substances:
        if d["id"] == drug_id:
            return d
    raise HTTPException(status_code=404, detail="Drogue non trouvée")


# --- Root ---
@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API InfoDrogues — consultez /drugs pour commencer."}
