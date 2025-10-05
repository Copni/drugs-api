from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="InfoDrogues API",
    description="API de recherche inspirée d’OMDb — prévention contre la drogue (projet étudiant)",
    version="2.0.0"
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Clé d'accès privée ---
API_KEY = "ILoveDrugs"

# --- Données ---
substances = [
    {
        "id": "D001",
        "nom": "Cannabis (résine, herbe, huile, CBD)",
        "type": "Psychotrope / stupéfiant",
        "molecule": "THC, CBD",
        "effet": "Euphorie, relaxation, altération de la perception.",
        "risque": "Troubles cognitifs, dépendance psychique, effets pulmonaires.",
        "prix": "≈ 10 €/g",
        "dangerosite": 4,
        "addictif": 3,
        "poster": "https://example.com/cannabis.jpg"
    },
    {
        "id": "D002",
        "nom": "Cocaïne / Crack",
        "type": "Stimulant",
        "molecule": "Chlorhydrate de cocaïne",
        "effet": "Euphorie, hyperactivité, désinhibition.",
        "risque": "Troubles cardiovasculaires, psychose, dépendance élevée.",
        "prix": "≈ 66 €/g",
        "dangerosite": 5,
        "addictif": 4,
        "poster": "https://example.com/cocaine.jpg"
    },{
    "id": "D004",
    "nom": "Héroïne",
    "type": "Opioïde / stupéfiant",
    "molecule": "Diacétylmorphine",
    "effet": "Euphorie intense, sédation, somnolence.",
    "risque": "Dépendance physique, risque de surdose, infections.",
    "prix": "≈ 28 €/g",
    "dangerosite": 5,
    "addictif": 5,
    "poster": "https://example.com/heroine.jpg"
},
{
    "id": "D005",
    "nom": "MDMA / Ecstasy",
    "type": "Stimulant empathogène",
    "molecule": "3,4-Méthylènedioxyméthamphétamine",
    "effet": "Euphorie, empathie, énergie accrue.",
    "risque": "Hyperthermie, déshydratation, troubles psychiatriques.",
    "prix": "≈ 10 €/comprimé",
    "dangerosite": 4,
    "addictif": 3,
    "poster": "https://example.com/mdma.jpg"
},
{
    "id": "D006",
    "nom": "Kétamine",
    "type": "Anesthésique dissociatif",
    "molecule": "Chlorhydrate de kétamine",
    "effet": "Dissociation, hallucinations, analgésie.",
    "risque": "Perte de conscience, dépendance psychologique.",
    "prix": "≈ 40 €/g",
    "dangerosite": 3,
    "addictif": 2,
    "poster": "https://example.com/ketamine.jpg"
},
{
    "id": "D007",
    "nom": "Méthamphétamine (Crystal Meth)",
    "type": "Stimulant puissant",
    "molecule": "N-méthylamphétamine",
    "effet": "Euphorie intense, vigilance, perte d’appétit.",
    "risque": "Addiction rapide, lésions cérébrales, paranoïa.",
    "prix": "≈ 80 €/g",
    "dangerosite": 5,
    "addictif": 5,
    "poster": "https://www.jeunessesansdroguecanada.org/wp-content/uploads/2023/04/meth-featured.jpeg"
},
{
    "id": "D008",
    "nom": "GHB",
    "type": "Dépresseur du système nerveux",
    "molecule": "Acide gamma-hydroxybutyrique",
    "effet": "Détente, désinhibition, somnolence.",
    "risque": "Troubles respiratoires, perte de conscience, overdose.",
    "prix": "≈ 5 €/dose",
    "dangerosite": 4,
    "addictif": 3,
    "poster": "https://example.com/ghb.jpg"
},
{
    "id": "D009",
    "nom": "Psilocybine (Champignons hallucinogènes)",
    "type": "Hallucinogène naturel",
    "molecule": "Psilocybine",
    "effet": "Hallucinations visuelles, introspection, distorsion du temps.",
    "risque": "Bad trips, anxiété, confusion.",
    "prix": "≈ 15 €/g",
    "dangerosite": 2,
    "addictif": 1,
    "poster": "https://example.com/psilo.jpg"
},
{
    "id": "D010",
    "nom": "Amphétamine",
    "type": "Stimulant",
    "molecule": "Amphétamine",
    "effet": "Vigilance accrue, énergie, euphorie.",
    "risque": "Insomnie, anxiété, dépendance.",
    "prix": "≈ 20 €/g",
    "dangerosite": 4,
    "addictif": 4,
    "poster": "https://example.com/amphetamine.jpg"
},
{
    "id": "D011",
    "nom": "Popper (nitrite d’amyle)",
    "type": "Vasodilatateur / inhalant",
    "molecule": "Nitrite d’amyle",
    "effet": "Euphorie courte, relaxation musculaire.",
    "risque": "Maux de tête, perte de conscience, hypotension.",
    "prix": "≈ 10 €/flacon",
    "dangerosite": 2,
    "addictif": 1,
    "poster": "https://example.com/popper.jpg"
},
{
    "id": "D012",
    "nom": "Tabac",
    "type": "Stimulant légal",
    "molecule": "Nicotine",
    "effet": "Stimulation légère, détente.",
    "risque": "Cancer, maladies cardiovasculaires, dépendance forte.",
    "prix": "≈ 10 €/paquet",
    "dangerosite": 4,
    "addictif": 5,
    "poster": "https://example.com/tabac.jpg"
},
{
    "id": "D013",
    "nom": "Alcool (éthanol)",
    "type": "Dépresseur légal",
    "molecule": "Éthanol",
    "effet": "Désinhibition, euphorie, relaxation.",
    "risque": "Addiction, cirrhose, violences, accidents.",
    "prix": "≈ 1 €/verre",
    "dangerosite": 4,
    "addictif": 4,
    "poster": "https://example.com/alcool.jpg"
},
{
    "id": "D014",
    "nom": "Protoxyde d’azote (gaz hilarant)",
    "type": "Dissociatif / inhalant",
    "molecule": "N2O",
    "effet": "Euphorie brève, sensation de flottement.",
    "risque": "Asphyxie, carence en vitamine B12, troubles neurologiques.",
    "prix": "≈ 1 €/cartouche",
    "dangerosite": 3,
    "addictif": 2,
    "poster": "https://example.com/n2o.jpg"
},
{
    "id": "D015",
    "nom": "Codeine",
    "type": "Opioïde",
    "molecule": "Phosphate de codéine",
    "effet": "Soulagement de la douleur, somnolence.",
    "risque": "Dépendance, dépression respiratoire.",
    "prix": "≈ 5 €/comprimé",
    "dangerosite": 3,
    "addictif": 3,
    "poster": "https://example.com/codeine.jpg"
},
{
    "id": "D016",
    "nom": "Tramadol",
    "type": "Antalgique opioïde",
    "molecule": "Tramadol",
    "effet": "Soulagement de la douleur, euphorie légère.",
    "risque": "Dépendance, convulsions, dépression respiratoire.",
    "prix": "≈ 4 €/comprimé",
    "dangerosite": 3,
    "addictif": 3,
    "poster": "https://example.com/tramadol.jpg"
},
{
    "id": "D017",
    "nom": "Benzodiazépines (Valium, Xanax, etc.)",
    "type": "Sédatif / anxiolytique",
    "molecule": "Diazépam, alprazolam...",
    "effet": "Calme, somnolence, réduction de l’anxiété.",
    "risque": "Dépendance, somnolence, interactions dangereuses avec l’alcool.",
    "prix": "≈ 2 €/comprimé",
    "dangerosite": 3,
    "addictif": 4,
    "poster": "https://example.com/benzo.jpg"
},
{
    "id": "D018",
    "nom": "PCP (Phencyclidine)",
    "type": "Hallucinogène dissociatif",
    "molecule": "Phencyclidine",
    "effet": "Hallucinations, agressivité, dissociation.",
    "risque": "Psychoses, comportements violents, dépendance.",
    "prix": "≈ 50 €/g",
    "dangerosite": 5,
    "addictif": 4,
    "poster": "https://example.com/pcp.jpg"
}

]

# --- Vérif clé API ---
def check_auth(auth: str = Header(None)):
    if auth != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Clé d'accès invalide ou manquante.")

# --- Endpoint principal (style OMDb) ---
@app.get("/drug")
def search_drug(
    t: str | None = Query(None, description="Recherche par nom exact (comme ?t=Inception)"),
    i: str | None = Query(None, description="Recherche par ID unique (comme ?i=D001)"),
    s: str | None = Query(None, description="Recherche partielle (comme ?s=can)"),
    page: int = Query(1, ge=1, description="Numéro de page pour la pagination"),
    Authorization: str = Header(None)
):
    check_auth(Authorization)
    per_page = 2  # pagination (2 résultats par page)

    # Recherche par ID
    if i:
        for d in substances:
            if d["id"].lower() == i.lower():
                return d
        raise HTTPException(status_code=404, detail="Aucune drogue trouvée avec cet ID.")

    # Recherche par nom exact
    if t:
        for d in substances:
            if d["nom"].lower() == t.lower():
                return d
        raise HTTPException(status_code=404, detail="Aucune drogue trouvée avec ce nom exact.")

    # Recherche partielle
    if s:
        matches = [d for d in substances if s.lower() in d["nom"].lower()]
        start = (page - 1) * per_page
        end = start + per_page
        return {
            "Search": matches[start:end],
            "totalResults": len(matches),
            "Response": "True" if matches else "False"
        }

    # Aucun paramètre fourni
    raise HTTPException(status_code=400, detail="Paramètre manquant. Utilisez ?t=, ?i= ou ?s=")

# --- Root ---
@app.get("/")
def root():
    return {"message": "Bienvenue sur InfoDrogues API — compatible avec la structure OMDb."}
