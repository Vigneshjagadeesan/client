import csv
import subprocess
import os
import pandas as pd
import streamlit as st
from playwright.sync_api import sync_playwright

# Install playwright browsers on runtime if needed
subprocess.run(["playwright", "install", "chromium"])


def scrape_google_maps(search_query):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        search_url = (
            f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        )
        page.goto(search_url)
        page.wait_for_timeout(5000)

        listings = page.locator('div[role="article"]').all()

        for item in listings[:10]:
            try:
                item.click()
                page.wait_for_timeout(2000)

                name = (
                    page.locator("h1").first.inner_text()
                    if page.locator("h1").count() > 0
                    else "N/A"
                )

                address_button = page.locator('button[data-item-id="address"]')
                address = (
                    address_button.inner_text()
                    if address_button.count() > 0
                    else "N/A"
                )

                website_button = page.locator('a[data-item-id="authority"]')
                website = (
                    website_button.get_attribute("href")
                    if website_button.count() > 0
                    else "No Website Available"
                )

                phone_button = page.locator(
                    'button[data-tooltip="Copy phone number"]'
                )
                phone = (
                    phone_button.inner_text()
                    if phone_button.count() > 0
                    else "No Phone Available"
                )

                results.append(
                    {
                        "Name": name,
                        "Address": address,
                        "Website": website,
                        "Phone": phone,
                    }
                )
            except Exception:
                continue

        browser.close()
    return results


# --- STREAMLIT DASHBOARD UI ---
st.set_page_config(page_title="Local Business Finder", layout="wide")
st.title("📍 Local Business Data Dashboard")

col1, col2 = st.columns(2)
with col1:
    location = st.text_input("Location / Area:", "Velachery, Chennai")
with col2:
    category = st.text_input("Category:", "Digital Marketing Agency")

if st.button("🔍 Search & Extract Data"):
    query = f"{category} in {location}"
    with st.spinner(f"Scraping data for '{query}'..."):
        data = scrape_google_maps(query)

        if data:
            df = pd.DataFrame(data)
            st.success(f"Successfully extracted {len(data)} results!")

            # Display Data Table
            st.dataframe(df, use_container_width=True)

            # CSV Download Button
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv_data,
                file_name=f"{category}_{location}.csv",
                mime="text/csv",
            )
        else:
            st.error("No results found or error during scraping.")