# Scraper.py

import streamlit as st
import pandas as pd

# Import SerpAPI avec bascule vers le legacy si nécessaire
try:
    from serpapi import GoogleSearch
except ImportError:
    from serpapi.google_search import GoogleSearch

@st.cache_data(show_spinner=False)
def fetch_urls(query: str, api_key: str, location: str = "France", num: int = 50) -> list[str]:
    """
    Lance une recherche Google via SerpAPI et renvoie la liste d'URLs organiques.
    """
    params = {
        "engine": "google",
        "q": query,
        "location": location,
        "google_domain": "google.fr",
        "gl": "fr",
        "hl": "fr",
        "num": str(num),
        "api_key": api_key
    }
    search = GoogleSearch(params)
    data = search.get_dict()
    organic = data.get("organic_results", [])
    return [item.get("link") for item in organic if item.get("link")]

def main():
    st.set_page_config(page_title="Scraper SEO SerpAPI", layout="wide")
    st.title("🕷️ Scraper d'URLs SEO avec SerpAPI")
    st.markdown("Entrez votre requête Google (ex. `site:monsite.fr mot-clé`)")

    # 1. Saisie des paramètres
    query = st.text_input("Requête Google", value="site:exemple.fr")
    num   = st.slider("Nombre de résultats", min_value=10, max_value=100, step=10, value=50)
    api_key = st.secrets.get("serpapi_key", "")

    if not api_key:
        st.warning("Clé SerpAPI introuvable : ajoutez-la dans `.streamlit/secrets.toml` sous `serpapi_key`.")

    # 2. Lancement du scraping
    if st.button("🚀 Lancer le scraping") and api_key:
        with st.spinner("Recherche en cours…"):
            urls = fetch_urls(query, api_key, num=num)
        if urls:
            st.success(f"{len(urls)} URLs récupérées.")
            df = pd.DataFrame({"URL": urls})
            st.dataframe(df, use_container_width=True)

            # 3. Téléchargement CSV
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Télécharger les URLs au format CSV",
                data=csv,
                file_name="urls_scrapées.csv",
                mime="text/csv"
            )
        else:
            st.error("Aucun résultat organique trouvé pour cette requête.")

if __name__ == "__main__":
    main()
