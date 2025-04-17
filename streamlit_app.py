import streamlit as st
import pandas as pd

# Import SerpAPI avec fallback legacy
try:
    from serpapi import GoogleSearch
except ImportError:
    from serpapi.google_search import GoogleSearch

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
    return [item["link"] for item in data.get("organic_results", []) if item.get("link")]

def main():
    st.set_page_config(page_title="Scraper SEO SerpAPI", layout="wide")
    st.title("🕷️ Scraper d'URLs SEO avec SerpAPI")

    api_key = st.secrets.get("serpapi_key")
    if not api_key:
        st.error(
            "❌ Clé SerpAPI introuvable. "
            "Ajoutez `serpapi_key` dans `.streamlit/secrets.toml` "
            "ou via l’UI de déploiement."
        )
        st.stop()

    query = st.text_input("Requête Google", value="site:exemple.fr")
    num   = st.slider("Nombre de résultats", 10, 100, 50, 10)

    if st.button("🚀 Lancer le scraping"):
        with st.spinner("Recherche en cours…"):
            urls = fetch_urls(query, api_key, num=num)
        if urls:
            st.success(f"{len(urls)} URLs récupérées.")
            df = pd.DataFrame({"URL": urls})
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Télécharger CSV", csv, "urls.csv", "text/csv")
        else:
            st.warning("Aucun résultat trouvé.")

if __name__ == "__main__":
    main()
