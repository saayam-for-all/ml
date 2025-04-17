import requests
import pandas as pd
import os

# URLs of the CSV files
csv_urls = [
    "https://www.irs.gov/pub/irs-soi/eo1.csv",
    "https://www.irs.gov/pub/irs-soi/eo2.csv",
    "https://www.irs.gov/pub/irs-soi/eo3.csv",
    "https://www.irs.gov/pub/irs-soi/eo4.csv"
]

# Create a folder to save downloaded files (optional)
download_folder = "irs_ngos"
os.makedirs(download_folder, exist_ok=True)

# List to hold DataFrames
dataframes = []

# Download and load CSVs into pandas
for i, url in enumerate(csv_urls):
    filename = os.path.join(download_folder, f"eo{i+1}.csv")
    
    # Download the file
    print(f"Downloading {url}...")
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    # Load into pandas
    print(f"Reading {filename}...")
    df = pd.read_csv(filename, low_memory=False)
    dataframes.append(df)

# Combine all DataFrames
print("Combining all CSVs into one DataFrame...")
combined_df = pd.concat(dataframes, ignore_index=True)

# Save combined DataFrame to CSV
output_file = os.path.join(download_folder, "combined_eo.csv")
combined_df.to_csv(output_file, index=False)
print(f"Combined CSV saved to {output_file}")
