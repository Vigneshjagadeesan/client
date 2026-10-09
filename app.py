import re
import pandas as pd
from serpapi import GoogleSearch
import streamlit as st


def search_places_serpapi(category, location, api_key):
    query = f"{category} in {location}"

    params = {
        "engine": "google_maps",
        "q": query,
        "api_key": api_key,
        "hl": "en",
        "gl": "in",
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    place_results = results.get("local_results", [])

    data = []
    for place in place_results:
        name = place.get("title", "N/A")
        address = place.get("address", "N/A")
        phone = place.get("phone", "N/A")
        website = place.get("website", "No Website Available")
        category_name = place.get("type", category)

        data.append(
            {
                "Name": name,
                "Category": category_name,
                "Website": website,
                "Phone": phone,
                "Address": address,
            }
        )

    return data


# --- STREAMLIT DASHBOARD UI ---
st.set_page_config(
    page_title="Local Business Data Extractor", layout="wide"
)

st.title("📍 Local Business Scraper & Lead Extractor")
st.write(
    "Extract business details like Name, Phone, Address, and Website instantly!"
)

# API Key Input
api_key = st.text_input(
    "🔑 Enter Your SerpAPI Key:",
    type="password",
    help="Get free key from serpapi.com",
)

col1, col2 = st.columns(2)
with col1:
    location = st.text_input("Location / Area:", "Velachery, Chennai")
with col2:
    category = st.text_input("Category:", "hospital")

if st.button("🔍 Search & Extract Data"):
    if not api_key:
        st.warning("Please enter your SerpAPI Key to run the search.")
    else:
        with st.spinner("Fetching verified details from Google Maps..."):
            try:
                data = search_places_serpapi(category, location, api_key)

                if data:
                    df = pd.DataFrame(data)
                    st.success(f"Found {len(data)} verified results!")

                    # Display Table
                    st.dataframe(df, use_container_width=True)

                    # CSV Download
                    csv_data = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Download Results as CSV (Excel)",
                        data=csv_data,
                        file_name=f"{category}_{location}.csv".replace(
                            " ", "_"
                        ),
                        mime="text/csv",
                    )
                else:
                    st.warning("No results found for this query.")
            except Exception as e:
                st.error(f"Error fetching data: {e}")
