# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import time

# Base URL for GuideStar Education and Training NGOs
base_url = "https://give.org/search/?term=education"

# Fetch and scrape data
data = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
} 

session = requests.Session()
session.headers.update(headers)

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
    ngos = soup.find_all("div", class_="result")  # Adjust class based on actual HTML structure
    
    if not ngos:
        print(f"No listings found on page {page}")
        continue  # Stop if no more NGOs are found

    for ngo in ngos:
            serial_id = len(data) + 1  # To get Unique IDs
            # Name
            name_tag = ngo.find("h6", class_="result__title")
            name = name_tag.get_text(strip=True) if name_tag else "N/A"
            
            # Description
            desc_tag = ngo.find("p", class_="result__entry")
            description = desc_tag.get_text(strip=True) if desc_tag else "N/A"
            
            # Location
            location_tag = ngo.find("div", class_="result__location")
            if location_tag:
                location_tag = ngo.find("div", class_="result__location")
if location_tag:
    full_address = location_tag.get_text(strip=True)
    
    # Split the address into parts
    address_parts = full_address.split(",")
    
    # Extract the address and city
    if len(address_parts) >= 2:
        address = address_parts[0].strip()  # Full address (e.g., "1175 Peachtree Road NE, 10th Floor")
        city_state_zip = address_parts[1].strip()  # Remaining part (e.g., "Atlanta, GA 30361")
        
        # Further split city, state, and zip
        city_state_zip_parts = city_state_zip.split(" ")
        city = " ".join(city_state_zip_parts[:-2])  # All parts except the last two are the city
        state = city_state_zip_parts[-2] if len(city_state_zip_parts) >= 2 else "N/A"  # Second last part is the state
        zip_code = city_state_zip_parts[-1] if len(city_state_zip_parts) >= 1 else "N/A"  # Last part is the zip code

        url_tag = ngo.find("a", class_="search-result-link")
        org_url = url_tag["href"] if url_tag and "href" in url_tag.attrs else "N/A"
        category = "Education"

        data.append([serial_id, name, city, state, org_url, category, description])
        
        page += 1
        time.sleep(2)  # Avoid rate limiting

    # Save to CSV
    if data:
        with open("Education_ngos_guidestar.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Org_ID", "Name", "City", "State", "Country", "URL", "Category", "Description"])  # Header
            writer.writerows(data)
        print("Data saved to Education_ngos_guidestar.csv")
    else:
        print("No data scraped.") 
        '''