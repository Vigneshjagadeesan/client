import re
from duckduckgo_search import DDGS
import pandas as pd
import requests
import streamlit as st


def find_contact_info(url):
    """Fetches the website HTML and extracts Email and Phone using Regex."""
    email, phone = "N/A", "N/A"
    if not url or url == "N/A" or not url.startswith("http"):
        return email, phone

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }
        res = requests.get(url, headers=headers, timeout=5)
        text = res.text

        # Extract Email using Regex
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text
        )
        if emails:
            # Filter common junk/image emails
            valid_emails = [
                e
                for e in emails
                if not e.endswith((".png", ".jpg", ".webp", ".svg"))
            ]
            if valid_emails:
                email = valid_emails[0]

        # Extract Phone Number using Regex (Indian Format)
        phones = re.findall(
            r"(?:\+91[\-\s]?)?[6-9]\d{9}|\b0\d{2,4}[\-\s]?\d{6,8}\b", text
        )
        if phones:
            phone = phones[0]

    except Exception:
        pass

    return email, phone


def scrape_businesses(query):
    results = []
    try:
        with DDGS() as ddgs:
            ddgs_results = list(
                ddgs.text(query, max_results=10, region="in-en")
            )

            for item in ddgs_results:
                name = item.get("title", "N/A")
                website = item.get("href", "N/A")
                snippet = item.get("body", "N/A")

                # Deep scan website for email and phone
                email, phone = find_contact_info(website)

                results.append(
                    {
                        "Name": name,
                        "Website": website,
                        "Email": email,
                        "Phone": phone,
                        "Address / Snippet Info": snippet,
                    }
                )
    except Exception as e:
        st.error(f"Search error: {e}")

    return results


# --- STREAMLIT DASHBOARD UI ---
st.set_page_config(
    page_title="Local Business Data Extractor", layout="wide"
)

st.title("📍 Local Business Scraper & Lead Extractor")
st.write(
    "Extract business name, website, phone, email, and address details"
    " instantly!"
)

col1, col2 = st.columns(2)
with col1:
    location = st.text_input("Location / Area:", "Velachery, Chennai")
with col2:
    category = st.text_input("Category:", "Digital Marketing Agency")

if st.button("🔍 Search & Extract Data"):
    search_query = f"{category} in {location}"
    with st.spinner(
        f"Scanning websites for Phone & Email in '{search_query}'..."
    ):
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
