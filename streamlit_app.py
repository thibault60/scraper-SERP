# streamlit_app.py

import streamlit as st
import pandas as pd
from github import Github  # veillez à avoir "PyGithub" dans requirements.txt
from serpapi import GoogleSearch
import requests

# ────────────────────────────────────────────────────
# 1. Gestion des secrets (.streamlit/secrets.toml)
# ────────────────────────────────────────────────────
# Créez un fichier .streamlit/secrets.toml contenant :
# serpapi_key = "VOTRE_CLE_SERPAPI"
SERPAPI_KEY = st.secrets["serpapi_key"]

# ────────────────────────────────────────────────────
# 2. Lecture de queries.txt depuis GitHub (public)
# ────────────────────────────────────────────────────
github = Github()  # accès en lecture seule aux dépôts publics
repo = github.get_repo("thibault60/scraper-SERP")
contents = repo.get_contents("queries.txt")
raw_txt = requests.get(contents.download_url).text

# Chaque ligne de queries.txt est considérée comme une requête
queries = [line.strip() for line in raw_txt.splitlines() if line.strip()]

# ────────────────────────────────────────────────────
# 3. Fonction d’extraction de la position zéro
# ────────────────────────────────────────────────────
def get_featured_snippet(query: str) -> dict:
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "fr",
        "gl": "fr",
        "num": 10,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    # SerpApi renvoie le featured snippet sous "answer_box" ou "featured_snippet"
    return results.get("answer_box") or results.get("featured_snippet") or {}

# ────────────────────────────────────────────────────
# 4. Mise en cache pour limiter les appels
# ────────────────────────────────────────────────────
@st.cache_data
def fetch_snippets(queries_list: list[str]) -> pd.DataFrame:
    records = []
    for q in queries_list:
        fs = get_featured_snippet(q)
        texte = fs.get("snippet") or fs.get("answer") or "—"
        records.append({"Requête": q, "Position zéro": texte})
    return pd.DataFrame(records)

# ────────────────────────────────────────────────────
# 5. Interface Streamlit
# ────────────────────────────────────────────────────
st.set_page_config(page_title="Positions Zéro SERP", layout="wide")
st.title("📊 Extraction des Positions Zéro – scraper-SERP")
st.markdown(
    "Cette app lit queries.txt depuis GitHub, interroge SerpApi et affiche "
    "les featured snippets (positions zéro)."
)

if st.button("🕹️ Extraire les featured snippets"):
    df_snippets = fetch_snippets(queries)
    st.dataframe(df_snippets, use_container_width=True)

    for _, row in df_snippets.iterrows():
        st.markdown("---")
        st.subheader(f"🔍 {row['Requête']}")
        if row["Position zéro"] != "—":
            st.markdown(row["Position zéro"])
        else:
            st.info("Pas de featured snippet trouvé pour cette requête.")
