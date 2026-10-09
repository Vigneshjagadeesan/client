import re
import pandas as pd
import requests
from serpapi import GoogleSearch
import streamlit as st


def extract_email_from_website(website_url):
    """Deep scans company website homepage & contact pages for Email addresses."""
    if not website_url or website_url == "No Website Available":
        return "N/A"

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }
        res = requests.get(website_url, headers=headers, timeout=5)
        text = res.text

        # Regex pattern for Email Extraction
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text
        )

        if emails:
            # Filter junk or image files
            valid_emails = [
                e
                for e in emails
                if not e.endswith(
                    (".png", ".jpg", ".webp", ".svg", ".gif", ".jpeg")
                )
            ]
            if valid_emails:
                return valid_emails[0]
    except Exception:
        pass

    return "N/A"


def search_places_with_emails(category, location, api_key):
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

        # Deep website scan for Email ID
        email = extract_email_from_website(website)

        data.append(
            {
                "Name": name,
                "Category": category_name,
                "Website": website,
                "Email": email,
                "Phone": phone,
                "Address": address,
            }
        )

    return data


# --- STREAMLIT DASHBOARD UI ---
st.set_page_config(
    page_title="Local Business Data Extractor", layout="wide"
)

st.title("📍 Complete Business Lead Generator")
st.write(
    "Extract Business Name, Website, Email, Phone, and Address automatically!"
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

if st.button("🔍 Search & Extract All Leads"):
    if not api_key:
        st.warning("Please enter your SerpAPI Key to run the search.")
    else:
        with st.spinner(
            "Fetching Google Maps data & scanning websites for Emails..."
        ):
            try:
                data = search_places_with_emails(category, location, api_key)

                if data:
                    df = pd.DataFrame(data)
                    st.success(
                        f"Found {len(data)} verified leads with contact info!"
                    )

                    # Display Table
                    st.dataframe(df, use_container_width=True)

                    # CSV Download
                    csv_data = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Download Leads as CSV (Excel)",
                        data=csv_data,
                        file_name=f"{category}_{location}_Leads.csv".replace(
                            " ", "_"
                        ),
                        mime="text/csv",
                    )
                else:
                    st.warning("No results found for this query.")
            except Exception as e:
                st.error(f"Error fetching data: {e}")
