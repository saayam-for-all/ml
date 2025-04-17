import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL
base_url_template = (
    "https://ngobase.org/c/{country_code}/{country_name}-ngos-charities?page={page}"
)

# Country details
africa_countries = {
    "DZ": {"name": "algeria", "pages": 5},
    "AO": {"name": "angola", "pages": 4},
    "BJ": {"name": "benin", "pages": 2},
    "BW": {"name": "botswana", "pages": 8},
    "BF": {"name": "burkina-faso", "pages": 17},
    "BI": {"name": "burundi", "pages": 3},
    "CM": {"name": "cameroon", "pages": 14},
    "CV": {"name": "cape-verde", "pages": 2},
    "CF": {"name": "central-african-republic", "pages": 3},
    "TD": {"name": "chad", "pages": 3},
    "KM": {"name": "comoros", "pages": 2},
    "CD": {"name": "congo-democratic-republic", "pages": 13},
    "CG": {"name": "congo", "pages": 1},
    "CI": {"name": "cote-divoire", "pages": 11},
    "DJ": {"name": "djibouti", "pages": 3},
    "EG": {"name": "egypt", "pages": 13},
    "GQ": {"name": "equatorial-guinea", "pages": 1},
    "ER": {"name": "eritrea", "pages": 1},
    "ET": {"name": "ethiopia", "pages": 17},
    "GA": {"name": "gabon", "pages": 4},
    "GM": {"name": "gambia", "pages": 5},
    "GH": {"name": "ghana", "pages": 5},
    "GN": {"name": "guinea", "pages": 6},
    "GW": {"name": "guinea-bissau", "pages": 1},
    "KE": {"name": "kenya", "pages": 9},
    "LS": {"name": "lesotho", "pages": 2},
    "LR": {"name": "liberia", "pages": 10},
    "LY": {"name": "libya", "pages": 9},
    "MG": {"name": "madagascar", "pages": 3},
    "MW": {"name": "malawi", "pages": 34},
    "ML": {"name": "mali", "pages": 16},
    "MR": {"name": "mauritania", "pages": 2},
    "MU": {"name": "mauritius", "pages": 6},
    "MA": {"name": "morocco", "pages": 4},
    "MZ": {"name": "mozambique", "pages": 13},
    "NA": {"name": "namibia", "pages": 20},
    "NE": {"name": "niger", "pages": 12},
    "NG": {"name": "nigeria", "pages": 35},
    "RW": {"name": "rwanda", "pages": 4},
    "SN": {"name": "senegal", "pages": 10},
    "SC": {"name": "seychelles", "pages": 1},
    "SL": {"name": "sierra-leone", "pages": 14},
    "SO": {"name": "somalia", "pages": 21},
    "ZA": {"name": "south-africa", "pages": 16},
    "SS": {"name": "south-sudan", "pages": 14},
    "SD": {"name": "sudan", "pages": 13},
    "SZ": {"name": "swaziland", "pages": 4},
    "TZ": {"name": "tanzania", "pages": 40},
    "TG": {"name": "togo", "pages": 3},
    "TN": {"name": "tunisia", "pages": 2},
    "UG": {"name": "uganda", "pages": 72},
    "ZM": {"name": "zambia", "pages": 22},
    "ZW": {"name": "zimbabwe", "pages": 21},
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
for country_code, details in africa_countries.items():
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