from duckduckgo_search import DDGS
import pandas as pd
import streamlit as st


def scrape_businesses(query):
    results = []
    try:
        # DDGS (DuckDuckGo Search) - Free and No IP Blocks!
        with DDGS() as ddgs:
            ddgs_results = list(
                ddgs.text(query, max_results=15, region="in-en")
            )

            for item in ddgs_results:
                results.append(
                    {
                        "Name": item.get("title", "N/A"),
                        "Website": item.get("href", "N/A"),
                        "Details / Address": item.get("body", "N/A"),
                    }
                )
    except Exception as e:
        st.error(f"Search error: {e}")

    return results


# --- STREAMLIT DASHBOARD UI ---
st.set_page_config(
    page_title="Local Business Data Extractor", layout="wide"
)

st.title("📍 Local Business Scraper & Dashboard")
st.write("Extract business details instantly using free search engine API!")

col1, col2 = st.columns(2)
with col1:
    location = st.text_input("Location / Area:", "Velachery, Chennai")
with col2:
    category = st.text_input("Category:", "hospital")

if st.button("🔍 Search & Extract Data"):
    search_query = f"{category} in {location}"
    with st.spinner(f"Extracting data for '{search_query}'..."):
        data = scrape_businesses(search_query)

        if data:
            df = pd.DataFrame(data)
            st.success(f"Found {len(data)} results successfully!")

            # Display Data Table
            st.dataframe(df, use_container_width=True)

            # CSV Download Button
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Results as CSV (Excel)",
                data=csv_data,
                file_name=f"{category}_{location}.csv".replace(" ", "_"),
                mime="text/csv",
            )
        else:
            st.warning(
                "No results found. Try changing the search terms or location."
            )
