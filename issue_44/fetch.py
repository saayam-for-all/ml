import requests
import json

API_URL = "https://api.charitynavigator.org/graphql"  
HEADERS = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer YOUR_API_KEY",  # replace with your api key
}

QUERY = """
query GetNonprofits {
  publicSearchFaceted(
    term: "",
    states: [],
    sizes: [],
    causes: [],
    ratings: [],
    c3: false,
    result_size: 10,
    from: 0,
    beacons: [],
    advisories: [],
    order_by: "relevance"
  ) {
    results {
      ein
      name
      mission
      organization_url
      charity_navigator_url
      encompass_score
      encompass_star_rating
      encompass_publication_date
      cause
      street
      street2
      city
      state
      zip
      country
      highest_level_advisory
      highest_level_alert
      encompass_rating_id
      acronym
    }
    total_results
  }
}
"""

def fetch_nonprofits():
    response = requests.post(API_URL, headers=HEADERS, json={"query": QUERY})
    if response.status_code == 200:
        data = response.json()
        nonprofits = data["data"]["publicSearchFaceted"]["results"]
        for org in nonprofits:
            print(f"{org['name']} - {org['city']}, {org['state']} ({org['zip']})")
            print(f"URL: {org['organization_url']}")
            print(f"Category: {org.get('cause')}")
            print(f"Phone: N/A") 
            print(f"Address: {org.get('street', '')} {org.get('street2', '')}")
            print(f"Description: {org.get('mission')}")
            print("-" * 60)
    else:
        print(f"Query failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    fetch_nonprofits()

