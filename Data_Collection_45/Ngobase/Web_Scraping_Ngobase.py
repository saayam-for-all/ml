# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import json
import pandas as pd
import time

# Base URL
base_url = "https://ngobase.org/cwa/US/EDU/education-and-training-ngos-charities-united-states?page={}"

# Fetch and scrape data
data = []
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
} 

page = 1
while True:
    url = base_url.format(page)
    print(f"Scraping page {page}...")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        break  # Stop if there's an error (e.g., 404 for no more pages)

    soup = BeautifulSoup(response.text, "html.parser")
    ngos = soup.find_all("div", class_="my_border ngo_listing_div")

    if not ngos:
        print(f"No listings found on page {page}")
        continue

    for ngo in ngos:
        serial_id = len(data) + 1 # To get Unique IDs
        # Name
        name_tag = ngo.find("h3", class_="ngo_name")
        name = name_tag.get_text(strip=True) if name_tag else "N/A"
        # Description
        desc_tag = ngo.find("div", class_="row brief_intro_row")
        description = desc_tag.get_text(strip=True) if desc_tag else "N/A"
        

        # City, Country, and State (inferred)
        location_div = ngo.find("div", class_="col", itemprop="location")
        city, country, state = "N/A", "N/A", "N/A"
        if location_div:
            location_tags = location_div.find_all("a", class_="listing_locations")
            if len(location_tags) >= 1:
                city = location_tags[0].get_text(strip=True)  # First link is city
                # Infer state from city URL (e.g., /ci/US.VA.5/ contains "VA")
                city_url = location_tags[0]["href"]
                state_code = city_url.split("/")[2].split(".")[1] if len(city_url.split("/")) > 2 else "N/A"
                state = state_code if state_code.isalpha() and len(state_code) == 2 else "N/A"
            if len(location_tags) >= 2:
                country = location_tags[1].get_text(strip=True)  # Second link is country

        url_tag = ngo.find("a", itemprop="url")
        org_url = url_tag["href"] if url_tag and "href" in url_tag.attrs else "N/A"
        category="Education"

        data.append([serial_id, name,  city, state, country, org_url, category, description])
    page+=1
    time.sleep(2)  # Avoid rate limiting

# Save to CSV
if data:
    with open("Education_ngos_name.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Org_ID", "Name", "city", "state", "country", "URL", "Category", "Description"])  # Header
        writer.writerows(data)
    print("Data saved to Education_ngos_name.csv")
else:
    print("No data scraped.")