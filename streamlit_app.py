# app.py

import streamlit as st
import pandas as pd
from io import StringIO
import requests
from github import Github
from serpapi import GoogleSearch

# ─────────────────────────────────────────────────────────────────────────────
# 1. Gestion des secrets (fichier .streamlit/secrets.toml)
# ─────────────────────────────────────────────────────────────────────────────
# .streamlit/secrets.toml doit contenir :
# serpapi_key = "VOTRE_CLE_SERPAPI"

SERPAPI_KEY = st.secrets["serpapi_key"]

# ─────────────────────────────────────────────────────────────────────────────
# 2. Lecture de la liste de requêtes depuis GitHub (dépôt public)
# ─────────────────────────────────────────────────────────────────────────────
github = Github()  # pas de token requis pour un repo public
repo = github.get_repo("votre_user/scraper-SERP")    # remplacez "votre_user"
contents = repo.get_contents("queries.csv")          # chemin relatif dans le dépôt
raw_csv = requests.get(contents.download_url).text
df_queries = pd.read_csv(StringIO(raw_csv))          # DataFrame avec une colonne "query"

# ─────────────────────────────────────────────────────────────────────────────
# 3. Fonction d’extraction de la position zéro via SerpApi
# ─────────────────────────────────────────────────────────────────────────────
def get_featured_snippet(query: str) -> dict:
    """
    Interroge SerpApi pour la requête donnée et renvoie
    le featured snippet (answer_box) ou {} si absent.
    """
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "fr",    # langue : français
        "gl": "fr",    # géolocalisation : France
        "num": 10
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    # SerpApi stocke la position zéro sous "answer_box" ou "featured_snippet"
    return results.get("answer_box") or results.get("featured_snippet") or {}

# ─────────────────────────────────────────────────────────────────────────────
# 4. Mise en cache pour limiter les appels API
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def fetch_snippets(queries: pd.Series) -> pd.DataFrame:
    """
    Pour chaque requête, récupère le featured snippet et
    renvoie un DataFrame avec les colonnes "Requête" et "Position zéro".
    """
    snippets = []
    for q in queries:
        fs = get_featured_snippet(q)
        texte = fs.get("snippet") or fs.get("answer") or "—"
        snippets.append({"Requête": q, "Position zéro": texte})
    return pd.DataFrame(snippets)

# ─────────────────────────────────────────────────────────────────────────────
# 5. Interface utilisateur Streamlit
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Positions Zéro SERP", layout="wide")
st.title("📊 Extraction des Positions Zéro – scraper-SERP")
st.markdown(
    "Cette application lit vos requêtes depuis GitHub, "
    "interroge SerpApi et affiche les featured snippets (positions zéro)."
)

if st.button("🕹️ Extraire les featured snippets"):
    # Exécution et affichage du tableau
    df_snippets = fetch_snippets(df_queries["query"])
    st.dataframe(df_snippets, use_container_width=True)

    # Affichage détaillé par requête
    for _, row in df_snippets.iterrows():
        st.markdown(f"---")
        st.subheader(f"🔍 {row['Requête']}")
        if row["Position zéro"] != "—":
            st.markdown(row["Position zéro"])
        else:
            st.info("Pas de featured snippet trouvé pour cette requête.")
