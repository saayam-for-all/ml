import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://give.org/search/?term=education'
headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; YourBot/1.0; +http://yourdomain.com/bot)'
}
response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.content, 'html.parser')

charities = []
charity_listings = soup.find_all("div", class_="result") # Limit to 20 charities

for charity in charity_listings:
    # Extract Category
    category_tag = charity.find('p', class_='result__entry')
    category = category_tag.find('span', class_='result__entry--info').text.strip() if category_tag else 'N/A'

    if category == "Charity - Education and Literacy":
        name = charity.find("h6", class_="result__title").text.strip()
        link_tag = charity.find('a', class_='result__title')
        url = link_tag['href'] if link_tag else 'N/A'

        address_tag = charity.find("p", class_="result__location")
        address = address_tag.text.strip() if address_tag else 'N/A'

        description_tag = charity.find("p", class_="result__entry")
        description = description_tag.text.strip() if description_tag else 'N/A'

        charities.append({
                        'Name': name,
                        'URL': url,
                        'Category': category,
                        'Address': address,
                        'Description': description
        })

df = pd.DataFrame(charities)
df.to_csv("education_charities.csv", index=False)

print(f"Scraped {len(charities)} charities successfully and saved to 'education_charities.csv'.")


