import re
import urllib.parse
from bs4 import BeautifulSoup
import pandas as pd
import requests
import streamlit as st


def scan_contact_info(url):
    """Scrapes company homepage to extract Phone & Email using Regex."""
    email, phone = "N/A", "N/A"
    if not url or url == "N/A" or not url.startswith("http"):
        return email, phone

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }
        res = requests.get(url, headers=headers, timeout=4)
        text = res.text

        # Find Email
        emails = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text
        )
        if emails:
            valid_emails = [
                e
                for e in emails
                if not e.endswith(
                    (".png", ".jpg", ".webp", ".svg", ".gif", ".jpeg")
                )
            ]
            if valid_emails:
                email = valid_emails[0]

        # Find Phone (Indian Format)
        phones = re.findall(
            r"(?:\+91[\-\s]?)?[6-9]\d{9}|\b0\d{2,4}[\-\s]?\d{6,8}\b", text
        )
        if phones:
            phone = phones[0]

    except Exception:
        pass

    return email, phone


def search_duckduckgo_html(query):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    # Direct DuckDuckGo HTML endpoint (Doesn't block IP)
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

    response = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers=headers,
        timeout=10,
    )

    results = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        for result in soup.find_all("div", class_="result"):
            title_tag = result.find("a", class_="result__a")
            snippet_tag = result.find("a", class_="result__snippet")

            if title_tag:
                name = title_tag.text.strip()
                link = title_tag.get("href", "")

                # Clean DDG redirect URL to get actual website
                if "uddg=" in link:
                    actual_url = urllib.parse.unquote(
                        link.split("uddg=")[1].split("&")[0]
                    )
                else:
                    actual_url = link

                snippet = (
                    snippet_tag.text.strip()
                    if snippet_tag
                    else "No snippet available"
                )

                # Scan website for Email & Phone
                email, phone = scan_contact_info(actual_url)

                results.append(
                    {
                        "Name": name,
                        "Website": actual_url,
                        "Email": email,
                        "Phone": phone,
                        "Address / Snippet": snippet,
                    }
                )

                if len(results) >= 10:
                    break

    return results


# --- STREAMLIT DASHBOARD UI ---
st.set_page_config(
    page_title="Local Business Data Extractor", layout="wide"
)

st.title("📍 Local Business Scraper & Lead Extractor")
st.write("Extract business website, email, phone, and address details!")

col1, col2 = st.columns(2)
with col1:
    location = st.text_input("Location / Area:", "Velachery, Chennai")
with col2:
    category = st.text_input("Category:", "hospital")

if st.button("🔍 Search & Extract Data"):
    search_query = f"{category} in {location}"
    with st.spinner(f"Extracting leads for '{search_query}'..."):
        data = search_duckduckgo_html(search_query)

        if data:
            df = pd.DataFrame(data)
            st.success(f"Successfully extracted {len(data)} results!")

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
            st.warning("No results found. Try again or change search keywords.")
