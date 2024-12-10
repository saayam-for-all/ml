import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL
base_url_template = (
    "https://ngobase.org/c/{country_code}/{country_name}-ngos-charities?page={page}"
)

# Country details
countries = {
    "BH": {"name": "bahrain", "pages": 6},
    "AM": {"name": "armenia", "pages": 7},
    "BD": {"name": "bangladesh", "pages": 41},
    "BT": {"name": "bhutan", "pages": 3},
    "BN": {"name": "brunei", "pages": 3},
    "KH": {"name": "cambodia", "pages": 4},
    "CN": {"name": "china", "pages": 3},
    "CY": {"name": "cyprus", "pages": 4},
    "GE": {"name": "georgia", "pages": 9},
    "ID": {"name": "indonesia", "pages": 3},
    "IR": {"name": "iran", "pages": 2},
    "IQ": {"name": "iraq", "pages": 9},
    "IL": {"name": "israel", "pages": 3},
    "JP": {"name": "japan", "pages": 3},
    "JO": {"name": "jordan", "pages": 6},
    "KW": {"name": "kuwait", "pages": 3},
    "LA": {"name": "laos", "pages": 3},
    "LB": {"name": "lebanon", "pages": 15},
    "MV": {"name": "maldives", "pages": 3},
    "MN": {"name": "mongolia", "pages": 2},
    "MM": {"name": "myanmar(burma)", "pages": 6},
    "NP": {"name": "nepal", "pages": 4},
    "OM": {"name": "oman", "pages": 2},
    "PK": {"name": "pakistan", "pages": 164},
    "PL": {"name": "palestine", "pages": 11},
    "PI": {"name": "philippines", "pages": 6},
    "QA": {"name": "qatar", "pages": 3},
    "RU": {"name": "russia", "pages": 2},
    "SA": {"name": "saudia-arabia", "pages": 6},
    "SG": {"name": "singapore", "pages": 40},
    "KR": {"name": "south-korea", "pages": 2},
    "SY": {"name": "syria", "pages": 5},
    "TH": {"name": "thailand", "pages": 3},
    "TH": {"name": "thailand", "pages": 3},
    "TR": {"name": "turkey", "pages": 13},
    "AE": {"name": "united-arab-emirates", "pages": 7},
    "YE": {"name": "yemen", "pages": 5},
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
for country_code, details in countries.items():
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
