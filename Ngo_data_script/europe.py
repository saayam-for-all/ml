import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL
base_url_template = (
    "https://ngobase.org/c/{country_code}/{country_name}-ngos-charities?page={page}"
)

# Country details
europe_countries = {
    "AL": {"name": "albania", "pages": 11},
    "AD": {"name": "andorra", "pages": 2},
    "AT": {"name": "austria", "pages": 7},
    "BY": {"name": "belarus", "pages": 3},
    "BE": {"name": "belgium", "pages": 8},
    "BA": {"name": "bosnia-and-herzegovina", "pages": 3},
    "BG": {"name": "bulgaria", "pages": 3},
    "HR": {"name": "croatia", "pages": 3},
    "CZ": {"name": "czech-republic", "pages": 7},
    "DK": {"name": "denmark", "pages": 29},
    "EE": {"name": "estonia", "pages": 7},
    "FI": {"name": "finland", "pages": 6},
    "FR": {"name": "france", "pages": 61},
    "DE": {"name": "germany", "pages": 61},
    "GR": {"name": "greece", "pages": 27},
    "HU": {"name": "hungary", "pages": 2},
    "IS": {"name": "iceland", "pages": 3},
    "IE": {"name": "ireland", "pages": 22},
    "IT": {"name": "italy", "pages": 32},
    "LV": {"name": "latvia", "pages": 9},
    "LI": {"name": "liechtenstein", "pages": 10},
    "LT": {"name": "lithuania", "pages": 3},
    "LU": {"name": "luxembourg", "pages": 19},
    "MT": {"name": "malta", "pages": 19},
    "MD": {"name": "moldova", "pages": 9},
    "MC": {"name": "monaco", "pages": 10},
    "ME": {"name": "montenegro", "pages": 7},
    "NL": {"name": "netherlands", "pages": 6},
    "MK": {"name": "north-macedonia", "pages": 3},
    "NO": {"name": "norway", "pages": 27},
    "PL": {"name": "poland", "pages": 7},
    "PT": {"name": "portugal", "pages": 24},
    "RO": {"name": "romania", "pages": 10},
    "RU": {"name": "russia", "pages": 2}, 
    "SM": {"name": "san-marino", "pages": 2},
    "RS": {"name": "serbia", "pages": 3},
    "SK": {"name": "slovakia", "pages": 2},
    "SI": {"name": "slovenia", "pages": 2},
    "ES": {"name": "spain", "pages": 47},
    "SE": {"name": "sweden", "pages": 7},
    "CH": {"name": "switzerland", "pages": 64},
    "UA": {"name": "ukraine", "pages": 25},
    "GB": {"name": "united-kingdom", "pages": 22},
}


# Function to extract data from a single page
def scrape_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    ngos = soup.find_all("div", class_="my_border ngo_listing_div")

    names, work_areas, websites, facebook_links, locations = [], [], [], [], []

    for ngo in ngos:
        name_tag = ngo.find("h3", class_="ngo_name")
        name = name_tag.get_text(strip=True) if name_tag else "N/A"

        work_area_tags = ngo.find_all("li", class_="ngo_listing_work_area_li")
        work_area_list = [wa.get_text(" -> ", strip=True) for wa in work_area_tags]
        work_area = ", ".join(work_area_list) if work_area_list else "N/A"

        website_tag = ngo.find("a", title=lambda x: x and "website" in x.lower())
        facebook_tag = ngo.find("a", title=lambda x: x and "facebook" in x.lower())
        website = website_tag["href"] if website_tag else "N/A"
        facebook = facebook_tag["href"] if facebook_tag else "N/A"

        location_tags = ngo.find_all("a", class_="listing_locations")
        location = (
            ", ".join([loc.get_text(strip=True) for loc in location_tags])
            if location_tags
            else "N/A"
        )

        names.append(name)
        work_areas.append(work_area)
        websites.append(website)
        facebook_links.append(facebook)
        locations.append(location)

    return pd.DataFrame(
        {
            "Name": names,
            "Work Areas": work_areas,
            "Website": websites,
            "Facebook": facebook_links,
            "Location": locations,
        }
    )


# Loop through each country
for country_code, details in europe_countries.items():
    country_name = details["name"]
    max_pages = details["pages"]
    all_data = pd.DataFrame()

    for page in range(1, max_pages + 1):
        url = base_url_template.format(
            country_code=country_code, country_name=country_name, page=page
        )
        print(f"Scraping {url}")
        page_data = scrape_page(url)
        all_data = pd.concat([all_data, page_data], ignore_index=True)

    # Save data to a CSV file named after the country
    csv_filename = f"data/{country_name}_ngos.csv"
    all_data.to_csv(csv_filename, index=False)
    print(f"Data for {country_name.capitalize()} saved to {csv_filename}")