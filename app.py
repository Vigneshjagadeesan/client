import urllib.parse
from bs4 import BeautifulSoup
import pandas as pd
import requests
import streamlit as st


def scrape_google_businesses(query):
    # Standard User-Agent to simulate real browser request
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    response = requests.get(search_url, headers=headers)

    results = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract business blocks from search results
        for g in soup.find_all("div", class_="g"):
            title_elem = g.find("h3")
            link_elem = g.find("a")

            if title_elem and link_elem:
                name = title_elem.text
                website = link_elem.get("href", "N/A")

                # Extract snippet/address info
                snippet_elem = g.find("div", class_="VwiC3b")
                address_snippet = (
                    snippet_elem.text if snippet_elem else "Details in website"
                )

                if website.startswith("http"):
                    results.append(
                        {
                            "Name": name,
                            "Website": website,
                            "Address / Info": address_snippet,
                        }
                    )

    return results


# --- STREAMLIT DASHBOARD UI ---
st.set_page_config(
    page_title="Local Business Data Extractor", layout="wide"
)

st.title("📍 Local Business Scraper & Dashboard")
st.write(
    "Extract businesses, websites, and details instantly without browser"
    " dependency!"
)

col1, col2 = st.columns(2)
with col1:
    location = st.text_input("Location / Area:", "Velachery, Chennai")
with col2:
    category = st.text_input("Category:", "Digital Marketing Agency")

if st.button("🔍 Search & Extract Data"):
    search_query = f"{category} in {location}"
    with st.spinner(f"Extracting data for '{search_query}'..."):
        data = scrape_google_businesses(search_query)

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
