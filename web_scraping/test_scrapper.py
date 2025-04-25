# from bs4 import BeautifulSoup
# import pandas as pd
# import requests
# import re
# import json
# from word2number import w2n
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# import time


# # Get the max page number to scrape all the clothes charities 
# headers = {'User-Agent': 'Mozilla/5.0'}
# test_eins = ["133433452", "530196605", "135660870", "273521132", "363256096", "202370934", "131760110", "202370934"]
# test_urls = []
# url = "https://www.charitynavigator.org/ein/"
# for i in range(len(test_eins)):
#     test_urls.append(url + test_eins[i])


# # Test URL
# url = test_urls[0] 


# def scrape_charity_navigator_profile(url, headers=None):
#     # Set headers if not provided
#     if headers is None:
#         headers = {"User-Agent": "Mozilla/5.0"}

#     # Default value for fields
#     default = "N/A"
#     data = {
#         "Organization Name": default,
#         "Organization URL": default,
#         "Score": default,
#         "Review Name": default,
#         "Review Rating Value": default,
#         "Phone Number": default,
#         "Address": default,
#         "Location": default,
#         "EIN": default,
#         "Mission": default,
#         "Meta Data": default
#     }

#     # Step 1: Static HTML Parsing
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, "html.parser")

#     # Organization name
#     name_div = soup.find("div", attrs={"class": lambda x: x and "tw-flex tw-flex-row tw-items-center" in x})
#     if name_div:
#         name_text = name_div.get_text(strip=True)
#         if name_text and "Not Considered" not in name_text:
#             data["Organization Name"] = name_text
    
#     # JSON-LD structured data
#     script_tag = soup.find("script", type="application/ld+json")
#     if script_tag:
#         try:
#             json_data = json.loads(script_tag.string)
#             name = json_data.get('name', '').strip()
#             data["Organization Name"] = name if name else data["Organization Name"]
#             url_val = json_data.get('url', '').strip()
#             if url_val:
#                 data["Organization URL"] = url_val
#             review = json_data.get('review', [{}])[0]
#             if isinstance(review, dict):
#                 rn = review.get('name', '').strip()
#                 if rn:
#                     data["Review Name"] = rn
#                 rr = review.get('reviewRating', {})
#                 rating_val = rr.get('ratingValue', '')
#                 if rating_val:
#                     data["Review Rating Value"] = rating_val
#         except Exception:
#             pass

#     # Address
#     address_div = soup.find('div', class_='tw-grid tw-space-y-2 tw-grid-cols-1 tw-text-base tw-text-gray-600')
#     if address_div:
#         divs = address_div.find_all('div')
#         spans = address_div.find_all('span')
#         street_address = divs[0].get_text(strip=True) if divs else ''
#         city_zip = spans[0].get_text(strip=True) if spans else ''
#         full_address = f"{street_address}, {city_zip}".strip(", ")
#         if full_address and "Not Considered" not in full_address:
#             data["Address"] = full_address

#     # Phone number
#     phone = soup.find('a', href=lambda x: x and x.startswith('tel:'))
#     if phone:
#         phone_val = phone.get_text(strip=True)
#         if phone_val:
#             data["Phone Number"] = phone_val

#     # Location and EIN
#     info_block = soup.find('div', class_='tw-flex tw-flex-row tw-px-4 tw-items-center')
#     if info_block:
#         cleaned = info_block.get_text().replace("\xa0", " ").strip()
#         parts = cleaned.split("|")
#         location = parts[0].strip() if parts else ''
#         if location:
#             data["Location"] = location
#         ein_match = re.search(r'EIN:\s*([\d-]+)', cleaned)
#         if ein_match:
#             data["EIN"] = ein_match.group(1).strip()

#     # Extract Meta data rating for Impact & Measurement, Accountability & Finance, Culture & Community, Leadership & Adaptability
#     meta_data = dict()
    
#     # Extract section titles like "Impact & Measurement", etc.
#     category_headers = soup.find_all('div', class_='tw-text-3xl tw-pb-4 tw-flex-col md:tw-w-3/5')
#     category_names = [header.get_text(strip=True) for header in category_headers]

#     # Extract associated scores or status for each category
#     category_scores = []

#     for score_block in soup.find_all('div', class_='tw-text-center md:tw-min-w-[280px] tw-min-w-auto'):
#         score_value = score_block.find('h3')
#         if score_value:
#             category_scores.append(score_value.get_text(strip=True))
#         else:
#             # Handle cases like "Not Currently Scored"
#             category_scores.append(score_block.get_text(strip=True))
    
#     # Combine category names and scores into meta_data
#     for category, score in zip(category_names, category_scores):
#         meta_data[category] = int(score) if score.isdigit() else "N/A"
    
#     data['Meta Data'] = meta_data

#     # Extract Organization Score out of 100
    
#     score_container = soup.find('div', class_='tw-flex tw-flex-col tw-p-2 tw-items-center tw-text-center tw-mt-5')
#     if score_container:
#         inner_div = score_container.find('div', class_='tw-p-6 tw-text-6xl tw-text-center')
#         if inner_div:
#             score = inner_div.get_text(strip=True).replace('%', '')
#             data['Score'] = int(score)
#         else:
#             data['Score'] = "N/A"
#     else:
#         print("Container not found")
#         data['Score'] = "N/A"


#     try:
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")  # Optional: Run in headless mode (no GUI)
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#         driver.get(url)
#         # Wait for the page to load (optional, depending on the page load time)

#         time.sleep(2)
#         # Locate and click the "More" link to expand the mission
#         more_button = driver.find_element(By.XPATH, "//span[contains(text(), '(More)')]")
#         more_button.click()
#         # Wait for the mission content to expand
#         time.sleep(2)

#         # Extract the full organization mission text
#         mission_text = driver.find_element(By.XPATH, "//div[contains(@class, 'tw-font-semibold') and contains(text(), 'Organization Mission')]/following-sibling::span").text
#         mission_text = mission_text.strip()
#         # Remove "(Less)" from the mission text
#         cleaned_mission_text = mission_text.replace(" (Less)", "")
#         data["Mission"] = cleaned_mission_text

#         # Close driver
#         driver.quit()
#     except Exception as e:
#         print("Selenium error:", e)
    
    

#     return data

# result = scrape_charity_navigator_profile(url)
# print(result)


# import time
# import json
# import pickle
# import requests
# from bs4 import BeautifulSoup
# import re
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Initialize cache for previously scraped data
# cache_file = "scraped_data_cache.pkl"

# # Load cache if it exists
# try:
#     with open(cache_file, "rb") as f:
#         cache = pickle.load(f)
# except FileNotFoundError:
#     cache = {}

# # Limit the number of requests per session
# MAX_REQUESTS_PER_RUN = 10  # Example limit, you can adjust this number
# REQUEST_DELAY = 2  # Delay between requests in seconds

# headers = {'User-Agent': 'Mozilla/5.0'}
# test_eins = ["133433452", "530196605", "135660870", "273521132", "363256096", "202370934", "131760110", "202370934", "133433452"]
# test_urls = []
# url = "https://www.charitynavigator.org/ein/"
# for i in range(len(test_eins)):
#     test_urls.append(url + test_eins[i])

# def scrape_charity_navigator_profile(url, headers=None):
#     if headers is None:
#         headers = {"User-Agent": "Mozilla/5.0"}

#     default = "N/A"
#     data = {
#         "Organization Name": default,
#         "Organization URL": default,
#         "Score": default,
#         "Review Name": default,
#         "Review Rating Value": default,
#         "Review URL": default,
#         "Phone Number": default,
#         "Address": default,
#         "Location": default,
#         "EIN": default,
#         "Mission": default,
#         "Meta Data": default
#     }

#     # Check if the URL is already cached
#     if url in cache:
#         print(f"Cache hit for {url}")
#         return cache[url]

#     # Step 1: Static HTML Parsing
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, "html.parser")

#     # Organization name
#     name_div = soup.find("div", attrs={"class": lambda x: x and "tw-flex tw-flex-row tw-items-center" in x})
#     if name_div:
#         name_text = name_div.get_text(strip=True)
#         if name_text and "Not Considered" not in name_text:
#             data["Organization Name"] = name_text
    
#     # JSON-LD structured data
#     script_tag = soup.find("script", type="application/ld+json")
#     if script_tag:
#         try:
#             json_data = json.loads(script_tag.string)
#             name = json_data.get('name', '').strip()
#             data["Organization Name"] = name if name else data["Organization Name"]
#             url_val = json_data.get('url', '').strip()
#             if url_val:
#                 data["Organization URL"] = url_val
#             review = json_data.get('review', [{}])[0]
#             if isinstance(review, dict):
#                 rn = review.get('name', '').strip()
#                 if rn:
#                     data["Review Name"] = rn
#                 rr = review.get('reviewRating', {})
#                 rating_val = rr.get('ratingValue', '')
#                 if rating_val:
#                     data["Review Rating Value"] = rating_val
#         except Exception:
#             pass

#     # Address
#     address_div = soup.find('div', class_='tw-grid tw-space-y-2 tw-grid-cols-1 tw-text-base tw-text-gray-600')
#     if address_div:
#         divs = address_div.find_all('div')
#         spans = address_div.find_all('span')
#         street_address = divs[0].get_text(strip=True) if divs else ''
#         city_zip = spans[0].get_text(strip=True) if spans else ''
#         full_address = f"{street_address}, {city_zip}".strip(", ")
#         if full_address and "Not Considered" not in full_address:
#             data["Address"] = full_address

#     # Phone number
#     phone = soup.find('a', href=lambda x: x and x.startswith('tel:'))
#     if phone:
#         phone_val = phone.get_text(strip=True)
#         if phone_val:
#             data["Phone Number"] = phone_val

#     # Address and EIN
#     info_block = soup.find('div', class_='tw-flex tw-flex-row tw-px-4 tw-items-center')
#     if info_block:
#         cleaned = info_block.get_text().replace("\xa0", " ").strip()
#         parts = cleaned.split("|")
#         location = parts[0].strip() if parts else ''
#         if location:
#             data["Location"] = location
#         ein_match = re.search(r'EIN:\s*([\d-]+)', cleaned)
#         if ein_match:
#             data["EIN"] = ein_match.group(1).strip()

#     # Extract Meta data rating for Impact & Measurement, Accountability & Finance, Culture & Community, Leadership & Adaptability
            
#     meta_data = dict()
#     category_headers = soup.find_all('div', class_='tw-text-3xl tw-pb-4 tw-flex-col md:tw-w-3/5')
#     category_names = [header.get_text(strip=True) for header in category_headers]
#     category_scores = []
#     meta_data_container = soup.find_all('div', class_='tw-text-center md:tw-min-w-[280px] tw-min-w-auto')
#     for score_block in meta_data_container:
#         score_value = score_block.find('h3')
#         if score_value:
#             category_scores.append(score_value.get_text(strip=True))
#         else:
#             category_scores.append(score_block.get_text(strip=True))

#     for category, score in zip(category_names, category_scores):
#         meta_data[category] = int(score) if score.isdigit() else "N/A"
    

#     fiscal_year = None

#     for block in meta_data_container:
#         if 'FY' in block.text:
#             text = block.get_text(separator=" ", strip=True)
#             match = re.search(r'FY\s*([0-9]{4})', text)
#             if match:
#                 fiscal_year = match.group(1)
#                 break  # Stop after finding first FY


#     meta_data['Fiscal Year'] = fiscal_year  # Output: 2023

#     data['Meta Data'] = meta_data


#     score_container = soup.find('div', class_='tw-flex tw-flex-col tw-p-2 tw-items-center tw-text-center tw-mt-5')
#     if score_container:
#         inner_div = score_container.find('div', class_='tw-p-6 tw-text-6xl tw-text-center')
#         if inner_div:
#             score = inner_div.get_text(strip=True).replace('%', '')
#             data['Score'] = int(score)
#         else:
#             data['Score'] = "N/A"
#     else:
#         print("Container not found")
#         data['Score'] = "N/A"

#     # Reviewer URL: Chairty Nav URL
#     data["Review URL"] = url

#     # Using Selenium for Dynamic Data
#     try:
#         # Initialize Selenium WebDriver
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")  # Optional: Run in headless mode (no GUI)
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#         driver.get(url)

#         # Wait for the page to load and ensure mission text is available
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '(More)')]"))
#         )

#         # Locate and click the "More" link to expand the mission
#         more_button = driver.find_element(By.XPATH, "//span[contains(text(), '(More)')]")
#         more_button.click()

#         # Wait for the mission content to expand
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'tw-font-semibold') and contains(text(), 'Organization Mission')]/following-sibling::span"))
#         )

#         # Extract the full organization mission text
#         mission_text = driver.find_element(By.XPATH, "//div[contains(@class, 'tw-font-semibold') and contains(text(), 'Organization Mission')]/following-sibling::span").text
#         mission_text = mission_text.strip()
#         # Clean up the mission text and add it to data
#         cleaned_mission_text = mission_text.replace(" (Less)", "")
#         data["Mission"] = cleaned_mission_text

#         # Close driver
#         driver.quit()
#     except Exception as e:
#         print("Selenium error:", e)
    
#     # Cache the result
#     cache[url] = data
#     with open(cache_file, "wb") as f:
#         pickle.dump(cache, f)

#     return data


# def scrape_all_charities(test_urls, max_requests=MAX_REQUESTS_PER_RUN):
#     results = []
#     requests_made = 0  # Initialize the counter for requests made
#     for i, url in enumerate(test_urls[:max_requests]):
#         if requests_made >= max_requests:
#             print("Reached max request limit.")
#             break

#         if url in cache:
#             print(f"Skipping {url} (cache hit)")
#             continue  # Skip storing the cached result in the results list
#         else:
#             print(f"Scraping {i + 1}/{max_requests}...")
#             data = scrape_charity_navigator_profile(url)  # Scrape if not cached
#             results.append(data)  # Store the fresh scraped data
#             requests_made += 1  # Increment the counter after each request
        
#         time.sleep(REQUEST_DELAY)  # Respect the delay between requests

#     # Save only the fresh scraped results (not cached) to CSV
#     if results:
#         df = pd.DataFrame(results)
#         df.to_csv('/Users/rishabkhuba/Desktop/Saayam-for-all/ml/web_scraping/charity_profiles.csv', index=False)
#         print("Scraping completed and data saved to charity_profiles.csv")
#     else:
#         print("No new data scraped. No data saved to CSV.")


# # Run the scraper with a limit on the number of requests
# scrape_all_charities(test_urls)






# Import packages

import csv
import time
import json
import pickle
import random
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration Constants
MAX_REQUESTS_PER_RUN = 10  # Limit the number of requests per session
REQUEST_DELAY = 2  # Delay between requests in seconds
# Configuration Constants
MAX_REQUESTS_PER_RUN = 10  # Limit the number of requests per session
REQUEST_DELAY = 2  # Delay between requests in seconds (between 2 and 5)
BATCH_DELAY = 5  # Delay after processing a batch in seconds (5-10 seconds)

CACHE_FILE = "scraped_data_cache.pkl"
USER_AGENT = 'Mozilla/5.0'

# Initialize cache for previously scraped data
def load_cache():
    try:
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}

# Save cache data
def save_cache(cache):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)

# Scraping function for Charity Navigator profile
def scrape_charity_navigator_profile(url, headers=None):
    if headers is None:
        headers = {"User-Agent": USER_AGENT}

    # Simulate delay between requests (2-5 seconds)
    time.sleep(random.uniform(REQUEST_DELAY, 5))  # Randomized delay

    data = initialize_data_structure()

    # Check if URL is cached
    if url in cache:
        print(f"Cache hit for {url}")
        return cache[url]

    # Perform static HTML scraping
    scrape_static_html(url, data, headers)

    # Perform dynamic data scraping using Selenium
    scrape_dynamic_data(url, headers, data)

    # Save scraped data in cache
    cache[url] = data
    save_cache(cache)

    return data

# Initialize data structure for scraped data
def initialize_data_structure():
    default = "N/A"
    return {
        "Organization Name": default,
        "Organization URL": default,
        "Score": default,
        "Review Name": default,
        "Review Rating Value": default,
        "Review URL": default,
        "Phone Number": default,
        "Address": default,
        "Location": default,
        "EIN": default,
        "Mission": default,
        "Meta Data": default
    }

# Scraping static HTML elements
def scrape_static_html(url, data, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Organization Name
    name_div = soup.find("div", attrs={"class": lambda x: x and "tw-flex tw-flex-row tw-items-center" in x})
    if name_div:
        name_text = name_div.get_text(strip=True)
        if name_text and "Not Considered" not in name_text:
            data["Organization Name"] = name_text

    # JSON-LD structured data
    script_tag = soup.find("script", type="application/ld+json")
    if script_tag:
        extract_json_ld_data(script_tag, data)

    # Address and EIN
    scrape_address_and_ein(soup, data)

    # Meta Data for Impact & Measurement, Accountability & Finance, etc.
    extract_meta_data(soup, data)

    # Review Score
    extract_review_score(soup, data)

    # Phone numbers
    scrape_phone_numbers(soup, data)
    data["Review URL"] = url

# Extract JSON-LD structured data
def extract_json_ld_data(script_tag, data):
    try:
        json_data = json.loads(script_tag.string)
        data["Organization Name"] = json_data.get('name', data["Organization Name"])
        data["Organization URL"] = json_data.get('url', data["Organization URL"])
        review = json_data.get('review', [{}])[0]
        if isinstance(review, dict):
            data["Review Name"] = review.get('name', data["Review Name"])
            rating_val = review.get('reviewRating', {}).get('ratingValue', '')
            data["Review Rating Value"] = rating_val if rating_val else data["Review Rating Value"]
    except Exception:
        pass

# Scrape Phone Number
def scrape_phone_numbers(soup, data):
    phone_container = soup.find('a', href=lambda x: x and x.startswith('tel:'))
    if phone_container:
        phone_val = phone_container.get_text(strip=True)
        if phone_val:
            data["Phone Number"] = phone_val
        else:
            data["Phone Number"] = "N/A"
    else:
        data["Phone Number"] = "N/A"

# Scrape Address and EIN
def scrape_address_and_ein(soup, data):
    address_div = soup.find('div', class_='tw-grid tw-space-y-2 tw-grid-cols-1 tw-text-base tw-text-gray-600')
    if address_div:
        divs = address_div.find_all('div')
        spans = address_div.find_all('span')
        street_address = divs[0].get_text(strip=True) if divs else ''
        city_zip = spans[0].get_text(strip=True) if spans else ''
        full_address = f"{street_address}, {city_zip}".strip(", ")
        if full_address and "Not Considered" not in full_address:
            data["Address"] = full_address

    # Extract EIN
    info_block = soup.find('div', class_='tw-flex tw-flex-row tw-px-4 tw-items-center')
    if info_block:
        cleaned = info_block.get_text().replace("\xa0", " ").strip()
        parts = cleaned.split("|")
        location = parts[0].strip() if parts else ''
        if location:
            data["Location"] = location
        ein_match = re.search(r'EIN:\s*([\d-]+)', cleaned)
        if ein_match:
            data["EIN"] = ein_match.group(1).strip()

# Extract Meta Data (Impact, Accountability, etc.)
def extract_meta_data(soup, data):
    meta_data = dict()
    category_headers = soup.find_all('div', class_='tw-text-3xl tw-pb-4 tw-flex-col md:tw-w-3/5')
    category_names = [header.get_text(strip=True) for header in category_headers]
    category_scores = []
    meta_data_container = soup.find_all('div', class_='tw-text-center md:tw-min-w-[280px] tw-min-w-auto')

    for score_block in meta_data_container:
        score_value = score_block.find('h3')
        category_scores.append(score_value.get_text(strip=True) if score_value else score_block.get_text(strip=True))

    for category, score in zip(category_names, category_scores):
        meta_data[category] = int(score) if score.isdigit() else "N/A"
    
    # Extract fiscal year
    fiscal_year = extract_fiscal_year(meta_data_container)
    meta_data['Fiscal Year'] = fiscal_year
    data['Meta Data'] = meta_data

# Extract Fiscal Year from meta data container
def extract_fiscal_year(meta_data_container):
    for block in meta_data_container:
        if 'FY' in block.text:
            text = block.get_text(separator=" ", strip=True)
            match = re.search(r'FY\s*([0-9]{4})', text)
            if match:
                return match.group(1)
    return None

# Extract review score
def extract_review_score(soup, data):
    score_container = soup.find('div', class_='tw-flex tw-flex-col tw-p-2 tw-items-center tw-text-center tw-mt-5')
    if score_container:
        inner_div = score_container.find('div', class_='tw-p-6 tw-text-6xl tw-text-center')
        if inner_div:
            score = inner_div.get_text(strip=True).replace('%', '')
            data['Score'] = int(score)
        else:
            data['Score'] = "N/A"
    else:
        data['Score'] = "N/A"

# Scraping dynamic data using Selenium
def scrape_dynamic_data(url, headers, data):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)

        # Wait for "(More)" button and click it
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '(More)')]"))
        )
        more_button = driver.find_element(By.XPATH, "//span[contains(text(), '(More)')]")
        more_button.click()

        # Wait for expanded mission content
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                "//div[contains(@class, 'tw-font-semibold') and contains(text(), 'Organization Mission')]/following-sibling::span"
            ))
        )

        # Extract mission text
        mission_text = driver.find_element(By.XPATH,
            "//div[contains(@class, 'tw-font-semibold') and contains(text(), 'Organization Mission')]/following-sibling::span"
        ).text

        cleaned_mission_text = mission_text.replace(" (Less)", "")
        data["Mission"] = cleaned_mission_text
        driver.quit()

    except Exception as e:
        print("Selenium error:", e)
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            # Fallback: Try to find mission text statically
            mission_header = soup.find("div", string="Organization Mission")
            if mission_header:
                parent = mission_header.find_parent("div")
                span_tag = parent.find("span")
                if span_tag:
                    mission_text = span_tag.get_text(strip=True)
                    data["Mission"] = mission_text
                else:
                    print("Mission <span> not found.")
                    data["Mission"] = "N/A"
            else:
                print("Mission text not found.")
                data["Mission"] = "N/A"

        except Exception as e:
            print("Selenium and fallback error:", e)
            data["Mission"] = "N/A"


        

def scrape_all_charities(test_urls, max_requests=MAX_REQUESTS_PER_RUN):
    results = []
    requests_made = 0  # Initialize the counter for requests made
    for i, url in enumerate(test_urls[:max_requests]):
        if requests_made >= max_requests:
            print("Reached max request limit.")
            break

        if url in cache:
            print(f"Skipping {url} (cache hit)")
            continue  # Skip storing the cached result in the results list
        else:
            # Scrape data for each URL
            print(f"Scraping {url}...")
            data = scrape_charity_navigator_profile(url)  # Scrape if not cached
            results.append(data)  # Store the fresh scraped data
            requests_made += 1  # Increment the counter after each request
        
       # Simulate delay after processing each batch (5-10 seconds)
        time.sleep(random.uniform(BATCH_DELAY, 10))  # Randomized batch delay

    # Save only the fresh scraped results (not cached) to CSV
    if results:
        df = pd.DataFrame(results)
        df.to_csv('./charity_profiles.csv', index=False)
        print("Scraping completed and data saved to charity_profiles.csv")
    else:
        print("No new data scraped. No data saved to CSV.")



# Main Execution: Initialize cache and scrape charities
cache = load_cache()
test_eins = ["133433452", "530196605", "135660870", "273521132", "363256096", "202370934", "131760110", "202370934", "133433452", "141849798", "942476942", "592906383", "592422998", "870643778"]
test_urls = [f"https://www.charitynavigator.org/ein/{ein}" for ein in test_eins]
csv_filename = "charity_profiles.csv"
scrape_all_charities(test_urls)