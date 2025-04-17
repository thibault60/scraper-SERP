import streamlit as st
from serpapi import GoogleSearch
import pandas as pd

# --- Fonction de scraping ---
@st.cache_data(show_spinner=False)
def fetch_urls(query: str, api_key: str, location: str="France", num: int=50) -> list[str]:
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
    return [item["link"] for item in organic if item.get("link")]

# --- Interface utilisateur ---
def main():
    st.set_page_config(page_title="Scraper SEO SerpAPI", layout="wide")
    st.title("🕷️ Scraper d'URLs avec SerpAPI")
    st.markdown("Entrez votre requête Google (ex. `site:monsite.fr mot-clé`)")

    query = st.text_input("Requête Google", value="site:exemple.fr")
    num   = st.slider("Nombre de résultats", 10, 100, 50, 10)
    api_key = st.secrets["serpapi_key"]

    if st.button("🚀 Scraper") and api_key:
        with st.spinner("Recherche…"):
            urls = fetch_urls(query, api_key, num=num)
        if urls:
            df = pd.DataFrame({"URL": urls})
            st.success(f"{len(urls)} URLs récupérées")
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Télécharger CSV", csv, "urls.csv", "text/csv")
        else:
            st.error("Aucun résultat trouvé")

if __name__ == "__main__":
    main()
