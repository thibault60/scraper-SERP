import streamlit as st
import pandas as pd
from io import StringIO
from github import Github
from serpapi import GoogleSearch
import requests

# 1. Clé SerpApi (dans .streamlit/secrets.toml)
SERPAPI_KEY = st.secrets["serpapi_key"]

# 2. Connexion GitHub (dépôt public)
github = Github()  # pas de token
repo = github.get_repo("votre_user/scraper-SERP")
contents = repo.get_contents("queries.txt")  # chemin relatif

# 3. Lecture du CSV depuis GitHub
raw_csv = requests.get(contents.download_url).text
df_queries = pd.read_csv(StringIO(raw_csv))

# 4. Extraction des featured snippets
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
    return results.get("answer_box") or results.get("featured_snippet") or {}

# 5. Interface Streamlit
st.title("Extraction des Positions Zéro depuis scraper-SERP")

if st.button("🕹️ Extraire les featured snippets"):
    snippets = []
    for q in df_queries["query"]:
        fs = get_featured_snippet(q)
        snippets.append({
            "Requête": q,
            "Position zéro": fs.get("snippet") or fs.get("answer") or "—"
        })
    df_snippets = pd.DataFrame(snippets)
    st.dataframe(df_snippets)

    for item in snippets:
        st.subheader(f"🔍 {item['Requête']}")
        if item["Position zéro"] != "—":
            st.markdown(item["Position zéro"])
        else:
            st.info("Pas de featured snippet trouvé pour cette requête.")
