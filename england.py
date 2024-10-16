import requests
import pandas as pd

# URL of the CSV export
url = "https://www.charitycommissionni.org.uk/umbraco/api/charityApi/ExportSearchResultsToCsv/?pageNumber=1"

# Send a GET request to the URL, disabling SSL verification
response = requests.get(url, verify=False)

# Check if the request was successful
if response.status_code == 200:
    # Save the content as a CSV file
    with open('england_charity_data.csv', 'wb') as file:
        file.write(response.content)
    print("File downloaded successfully!")
else:
    print(f"Failed to download file. Status code: {response.status_code}")

df = pd.read_csv('england_charity_data.csv', encoding='ISO-8859-1')

df = df.drop(['Date registered', 'Status', 'Date for financial year ending', 'Total income', 'Total expenditure', 'Total income. Previous financial period.', 'Total income and endowments', 'Total spending', 'Total net assets and liabilities', 'Assets and liabilities - Total fixed assets', 'Charitable spending', 'Income from charitable activities', 'Income from donations and legacies', 'Income from investments', 'Income from other', 'Income from other trading activities', 'Income generation and governance', 'Company number', 'Type of governing document', 'Financial period end', 'Financial period start', 'Unnamed: 38', 'Expenditure on Charitable activities', 'Expenditure on Governance', 'Expenditure on Other' ,'Expenditure on Raising funds', 'Employed staff', 'UK and Ireland volunteers' ], axis=1)

df.to_csv('england_charity_data.csv', index=False)