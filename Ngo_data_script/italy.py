from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Configure WebDriver
download_dir = r"C:\Users\hemil\PycharmProjects\pythonProject2\italy"   # Update this path
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,  # Set default download location
    "download.prompt_for_download": False,       # Disable download prompts
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,                # Enable safe browsing
}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)

try:
    # Open the website
    driver.get("https://servizi.lavoro.gov.it/runts/it-it/Lista-enti")
    wait = WebDriverWait(driver, 20)

    try:
        accept_cookies_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'footer-link') and contains(text(), 'ACCETTA')]"))
        )
        accept_cookies_button.click()
        print("Cookies accepted.")
    except Exception as e:
        print("No cookie banner found or already accepted:", str(e))

    time.sleep(10)

    # Locate the "Scarica" button
    scarica_button = wait.until(
        EC.presence_of_element_located((By.ID, "dnn_ctr428_View_gvEnti_btnScaricaDoc_2"))
    )

    # Scroll to the button to make it visible
    driver.execute_script("arguments[0].scrollIntoView();", scarica_button)

    # Optionally wait for the button to be clickable
    wait.until(EC.element_to_be_clickable((By.ID, "dnn_ctr428_View_gvEnti_btnScaricaDoc_2")))

    # Click the button using JavaScript to bypass obstructions
    driver.execute_script("arguments[0].click();", scarica_button)

    time.sleep(30)

finally:
    # Close the browserz`
    driver.quit()

# Verify download
downloaded_files = os.listdir(download_dir)
print("Downloaded files:", downloaded_files)


import pandas as pd

excel_file = None
for file in downloaded_files:
    if file.endswith(".xlsx"):  # Change to ".xls" if it's an older Excel format
        excel_file = os.path.join(download_dir, file)
        break

print(excel_file)
# Read the Excel file into a pandas DataFrame
if excel_file:
    df = pd.read_excel(excel_file, engine = 'openpyxl')
    print("Excel file loaded successfully:")
    print(df.head())  # Display the first few rows of the DataFrame
else:
    print("No Excel file found in the download folder.")

#Directly renaming the columns
df.columns = [
    "Tax Code",
    "Registry",
    "Name",
    "Section",
    "Legal Representative Surname",
    "Legal Representative Name",
    "Network",
    "Municipality Legal Headquarters",
    "Province Legal Headquarters",
    "5x1000",
    "Registration Date"
]

df.to_csv("italy.csv", index = False)