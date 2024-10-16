import requests
import pandas as pd

# URL to the dataset
url = 'https://open.canada.ca/data/dataset/08ae3944-1a9d-483a-a7ae-116bc58199fd/resource/3929647c-13f0-48b0-a295-6d73f23e47d7/download/ident_2021.csv'

# Local filename to save the file
output_file = 'canadian_charities_data.csv'  # You can rename it as needed

# Make a GET request to fetch the file
response = requests.get(url, stream=True)

# Check if the request was successful
if response.status_code == 200:
    # Open the output file in binary mode
    with open(output_file, 'wb') as file:
        # Write the file content in chunks
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"File downloaded successfully as '{output_file}'")
else:
    print(f"Failed to download file. HTTP Status Code: {response.status_code}")

# Second dataset URL
url = 'https://open.canada.ca/data/dataset/08ae3944-1a9d-483a-a7ae-116bc58199fd/resource/c2083feb-75e4-46ce-82f5-f854f380425e/download/weburl_2021.csv'

# Local filename to save the second file
output_file = 'charity_web_contact.csv'  # You can rename it as needed

# Make a GET request to fetch the second file
response = requests.get(url, stream=True)

# Check if the request was successful
if response.status_code == 200:
    # Open the output file in binary mode
    with open(output_file, 'wb') as file:
        # Write the file content in chunks
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"File downloaded successfully as '{output_file}'")
else:
    print(f"Failed to download file. HTTP Status Code: {response.status_code}")

# Read the downloaded CSV files with error handling (ignore bad lines)
df1 = pd.read_csv("canadian_charities_data.csv", encoding='ISO-8859-1', on_bad_lines='skip')
df2 = pd.read_csv("charity_web_contact.csv", encoding='ISO-8859-1', on_bad_lines='skip')

# Rename column in df2 if necessary to ensure it matches df1 for merging
df2.rename(columns={"BN/NE": "BN"}, inplace=True)

# Merge the two dataframes on the 'BN' column
merged_df = pd.merge(df1, df2, on='BN', how='inner')

# Save the merged dataframe to a new CSV file
merged_output_file = 'merged_charities_data.csv'
merged_df.to_csv(merged_output_file, index=False)

print(f"Merged data saved to {merged_output_file}")
