import requests
import pandas as pd


# URL of the CSV file
url = "https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/8fb32972-24e9-4c95-885e-7140be51be8a/download/datadotgov_main.csv"
# Send a GET request to download the file
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Save the file locally
    with open("dataset.csv", "wb") as file:
        file.write(response.content)
    print("CSV file downloaded successfully.")
else:
    print(f"Failed to download the file. Status code: {response.status_code}")


df = pd.read_csv('dataset.csv')

# Dropping columns that are not of use to us
df = df.drop(['Other_Organisation_Names', 'Address_Type', 'Registration_Date', 'Date_Organisation_Established', 'Financial_Year_End'], axis=1)

# Combining address columns
df['Address'] = df['Address_Line_1'].fillna('') + ', ' + df['Address_Line_2'].fillna('') + ', ' + df['Address_Line_3'].fillna('')
df['Address'] = df['Address'].str.rstrip(', ')
df = df.drop(['Address_Line_1', 'Address_Line_2', 'Address_Line_3'], axis = 1)

# Combining 'Operates_in_" columns
operating_columns = [col for col in df.columns if 'Operates_in' in col]
df['Operating_location_in_AUS'] = df.apply(
    lambda row: ', '.join([col.split(' ')[-1]
                           for col in operating_columns if row[col] == 'Y']), axis=1)
df['Operating_location_in_AUS'].str.replace('Operates_in_', '')
df = df.drop(operating_columns, axis=1)

# Combining all category columns under one umbrella column
column_indices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
df['Category'] = df.apply(lambda row: ', '.join([df.columns[i].split(' in ')[-1]
                                                             for i in column_indices if row[i] == 'Y']), axis=1)
df['Category'] = df['Category'].str.replace('PBI', "Public Benevolent Institution")
df['Category'] = df['Category'].str.replace('HPC', 'Health Promotion Charity')
df['Category'] = df['Category'].str.replace("Promote_or_oppose_a_change_to_law__government_poll_or_prac", "Promote_or_oppose_a_change_to_law - government, poll, or_practice")
df['Category'] = df['Category'].str.replace('_', " ")
df = df.drop(df.columns[column_indices], axis=1)

# Combining all beneficiaries column under one umbrella column
column_indices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
df['Beneficiaries'] = df.apply(lambda row: ', '.join([df.columns[i].split(' in ')[-1]
                                                             for i in column_indices if row[i] == 'Y']), axis=1)

df['Beneficiaries'] = df['Beneficiaries'].str.replace('_', " ")

df = df.drop(df.columns[column_indices], axis=1)

# Rearranging the columns
ad = df.pop('Address')
df.insert(2, "Address", ad)

#Writing final output to csv
df.to_csv('dataset.csv', index=False)

