import requests
import zipfile
import io
import os
import pandas as pd

# URL of the ZIP file
url = 'https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityRegDownload'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:

    # Open the response content as a ZIP file
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:

        # Extract all contents of the ZIP file into the 'scottish_charities' directory
        zip_ref.extractall('scottish_charities')

        # Loop through files and find the CSV file
        csv_file = None
        for file in zip_ref.namelist():
            if file.endswith('.csv'):
                csv_file = file
                print(f"CSV file found: {csv_file}")
                break

        # If a CSV file was found, load it into a Pandas DataFrame
        if csv_file:
            # Construct the file path for the extracted CSV
            csv_file_path = os.path.join('scottish_charities', csv_file)

            # Load the CSV file into a Pandas DataFrame
            df = pd.read_csv(csv_file_path, encoding='ISO-8859-1')  # Adjust encoding if necessary

            # Display the first few rows of the DataFrame
            df = df.drop(['Registered Date', 'Known As', 'Charity Status', 'Notes', 'Constitutional Form', 'Previous Constitutional Form 1', 'Geographical Spread', 'Most recent year income', 'Most recent year expenditure', 'Mailing cycle', 'Year End', 'Date annual return received', ' Next year end date', ' Donations and legacies income', 'Charitable activities income', 'Other trading activities income', 'Investments income', 'Other income', 'Raising funds spending', 'Charitable activities spending', 'Other spending', 'Parent charity name', 'Parent charity number', 'Parent charity country of registration', 'Designated religious body', 'Regulatory Type'], axis=1)
            df.to_csv('scotland_charity_data.csv', index=False)
else:
    print(f"Failed to download the file. HTTP Status Code: {response.status_code}")
