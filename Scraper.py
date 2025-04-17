# streamlit_app.py
import streamlit as st
from serpapi import GoogleSearch
import pandas as pd

# --- Fonctions utilitaires ---

@st.cache_data(show_spinner=False)
def fetch_urls(query: str, api_key: str, location: str="France", num: int=50) -> list[str]:
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
    # Extraction des URLs
    organic = data.get("organic_results", [])
    return [item.get("link") for item in organic if item.get("link")]

# --- Interface Streamlit ---

def main():
    st.set_page_config(page_title="Scraper SEO – SerpAPI", layout="wide")
    st.title("🕷️ Scraper d'URLs SEO avec SerpAPI")

    # 1. Saisie des paramètres
    st.markdown("**1. Paramètres de la recherche**")
    query = st.text_input("Requête Google (`q`)", value="site:exemple.fr")
    num    = st.slider("Nombre de résultats à récupérer", min_value=10, max_value=100, step=10, value=50)
    # on peut aussi récupérer la clé API depuis secrets.toml : 
    api_key = st.secrets.get("serpapi_key", "")  # Configurer dans .streamlit/secrets.toml

    if not api_key:
        st.warning("Vous n'avez pas configuré votre clé SerpAPI. Ajoutez-la dans `.streamlit/secrets.toml` sous `serpapi_key`.")

    # 2. Bouton de lancement
    if st.button("🚀 Lancer le scraping") and api_key:
        with st.spinner("Recherche en cours…"):
            urls = fetch_urls(query, api_key, num=num)
        if urls:
            st.success(f"{len(urls)} URLs récupérées.")
            df = pd.DataFrame({"URLs": urls})
            st.dataframe(df, use_container_width=True)

            # 3. Téléchargement CSV
            csv = df.to_csv(index=False).encode('utf-8')
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
