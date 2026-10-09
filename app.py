import re
import pandas as pd
import requests
from serpapi import GoogleSearch
import streamlit as st


# 1. Deep scan website for Email
def extract_email_from_website(website_url):
    if not website_url or website_url == "No Website Available":
        return "N/A"

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }
        res = requests.get(website_url, headers=headers, timeout=4)
        text = res.text

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
                return valid_emails[0]
    except Exception:
        pass

    return "N/A"


# 2. Multi-Page Google Maps Search (SerpAPI)
def search_google_maps_multipage(category, location, api_key, max_pages=3):
    query = f"{category} in {location}"
    all_results = []

    for page in range(max_pages):
        start_offset = page * 20
        params = {
            "engine": "google_maps",
            "q": query,
            "api_key": api_key,
            "hl": "en",
            "gl": "in",
            "start": start_offset,
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            place_results = results.get("local_results", [])

            if not place_results:
                break

            for place in place_results:
                name = place.get("title", "N/A")
                address = place.get("address", "N/A")
                phone = place.get("phone", "N/A")
                website = place.get("website", "No Website Available")
                category_name = place.get("type", category)

                # Scan website for Email ID
                email = extract_email_from_website(website)

                all_results.append(
                    {
                        "Name": name,
                        "Category": category_name,
                        "Website": website,
                        "Email": email,
                        "Phone": phone,
                        "Address": address,
                        "Source": f"Google Maps (Page {page + 1})",
                    }
                )
        except Exception:
            break

    return all_results


# --- STREAMLIT DASHBOARD UI ---
st.set_page_config(
    page_title="Ultimate Local Lead Extractor", layout="wide"
)

st.title("📍 Ultimate Business Lead Extractor (Multi-Page)")
st.write(
    "Extract top ranked and extended multi-page listings with Email, Phone,"
    " & Individual Copy Cards!"
)

# SerpAPI Key Input
api_key = st.text_input(
    "🔑 Enter Your SerpAPI Key:",
    type="password",
    help="Get free key from serpapi.com",
)

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    location = st.text_input("Location / Area:", "Velachery, Chennai")
with col2:
    category = st.text_input("Category:", "hospital")
with col3:
    pages = st.selectbox("Pages to Scan:", [1, 2, 3], index=2)

if st.button("🔍 Search & Extract All Leads"):
    if not api_key:
        st.warning("Please enter your SerpAPI Key to run the search.")
    else:
        with st.spinner(
            f"Scanning up to {pages * 20} leads & extracting emails..."
        ):
            try:
                data = search_google_maps_multipage(
                    category, location, api_key, max_pages=pages
                )

                if data:
                    df = pd.DataFrame(data)
                    st.success(f"Total Extracted Verified Leads: {len(data)}")

                    # Summary Table
                    st.subheader("📊 Combined Summary Table")
                    st.dataframe(df, use_container_width=True)

                    # CSV Download Button
                    csv_data = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Download All Leads as CSV (Excel)",
                        data=csv_data,
                        file_name=f"{category}_{location}_All_Leads.csv".replace(
                            " ", "_"
                        ),
                        mime="text/csv",
                    )

                    st.markdown("---")

                    # Individual Copy Cards
                    st.subheader("📋 Individual Lead Copy Cards")
                    st.caption(
                        "Click the copy button inside each box to quickly copy"
                        " Name, Email, or Phone Number!"
                    )

                    for idx, item in enumerate(data, 1):
                        with st.expander(
                            f"🏢 #{idx} - {item['Name']} ({item['Source']})",
                            expanded=False,
                        ):
                            c1, c2, c3, c4 = st.columns([2, 2, 2, 3])

                            with c1:
                                st.text_input(
                                    "Business Name",
                                    value=item["Name"],
                                    key=f"name_{idx}",
                                )
                            with c2:
                                st.text_input(
                                    "Email Address",
                                    value=item["Email"],
                                    key=f"email_{idx}",
                                )
                            with c3:
                                st.text_input(
                                    "Phone Number",
                                    value=item["Phone"],
                                    key=f"phone_{idx}",
                                )
                            with c4:
                                st.text_input(
                                    "Website / Address",
                                    value=f"{item['Website']} | {item['Address']}",
                                    key=f"info_{idx}",
                                )
                else:
                    st.warning("No results found for this query.")
            except Exception as e:
                st.error(f"Error fetching data: {e}")
