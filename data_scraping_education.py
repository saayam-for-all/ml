from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")

service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

all_data = []

for page_num in range(1, 3): 
    print(f"Scraping page {page_num}...")
    base_url = f"https://www.charitynavigator.org/search?page={page_num}&causes=Education"
    driver.get(base_url)
    time.sleep(5)

    for i in range(10):
        try:
            driver.get(base_url)
            time.sleep(4)

            cards = driver.find_elements(By.CSS_SELECTOR, "div[aria-label='nonprofit profile page']")
            if i >= len(cards):
                break

            card = cards[i]
            driver.execute_script("arguments[0].scrollIntoView();", card)
            time.sleep(1)

            name = card.find_element(By.TAG_NAME, "h2").text.strip()
            location = card.find_element(By.CLASS_NAME, "tw-text-base").text.strip()

            try:
                driver.execute_script("""
                    let popup = document.querySelector('getsitecontrol-widget');
                    if (popup) { popup.remove(); }
                """)
                time.sleep(1)

                profile_link_element = card.find_element(By.TAG_NAME, "h2")
                driver.execute_script("arguments[0].scrollIntoView(true);", profile_link_element)
                time.sleep(0.5)
                profile_link_element.click()
                time.sleep(4)

                try:
                    address_block = driver.find_element(By.CSS_SELECTOR, "div.tw-grid.tw-space-y-2")
                    address_lines = address_block.text.split('\n') 
                    address = ", ".join(address_lines)
                except NoSuchElementException:
                    address = ""

                try:
                    phone = driver.find_element(By.CSS_SELECTOR, "a[href^='tel']").text.strip()
                except NoSuchElementException:
                    phone = ""

                try:
                    website_element = driver.find_element(By.XPATH, "//div[contains(@class, 'tw-flex-1')]//a[contains(@class, 'cn-link-profile') and starts-with(@href, 'http')]")
                    website = website_element.get_attribute("href")
                except NoSuchElementException:
                    website = ""

                try:
                    more_button = driver.find_element(By.XPATH, "//span[contains(text(), '(More)')]")
                    driver.execute_script("arguments[0].click();", more_button)
                    time.sleep(1)  
                except NoSuchElementException:
                    pass  

                try:
                    mission_header = driver.find_element(By.XPATH, "//div[contains(@class, 'tw-px-4')]//div[text()='Organization Mission']")
                    mission_span = mission_header.find_element(By.XPATH, "following-sibling::span")
                    description = mission_span.text.strip()
                except NoSuchElementException:
                    description = ""



                all_data.append({
                    "Name": name,
                    "Location": location,
                    "Address": address,
                    "Phone Number": phone,
                    "URL": website,
                    "Description": description,
                    "Category": "Education"
                })

                driver.back()
                time.sleep(3)

            except Exception as e:
                print(f" Error visiting profile: {e}")
                continue

        except Exception as e:
            print(f" Error on card {i+1}: {e}")
            continue

driver.quit()

df = pd.DataFrame(all_data)
df.to_csv("data_collected.csv", index=False)
print(" Data saved to data.csv")
