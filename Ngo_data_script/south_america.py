import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL
base_url_template = (
    "https://ngobase.org/c/{country_code}/{country_name}-ngos-charities?page={page}"
)

# Country details
south_america_countries = {
    "AR": {"name": "argentina", "pages": 3},
    "BO": {"name": "bolivia", "pages": 3},
    "BR": {"name": "brazil", "pages": 3},
    "CL": {"name": "chile", "pages": 3},
    "CO": {"name": "colombia", "pages": 3},
    "EC": {"name": "ecuador", "pages": 3},
    "GY": {"name": "guyana", "pages": 3},
    "PY": {"name": "paraguay", "pages": 3},
    "PE": {"name": "peru", "pages": 3},
    "SR": {"name": "suriname", "pages": 2},
    "UY": {"name": "uruguay", "pages": 2},
    "VE": {"name": "venezuela", "pages": 3},
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
for country_code, details in south_america_countries.items():
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