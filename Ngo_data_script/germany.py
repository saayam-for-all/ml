import pandas as pd
from deep_translator import GoogleTranslator
import concurrent.futures

# Read the CSV file with semicolon separator
df = pd.read_csv('ZER--20241203.csv', sep=';', encoding='utf-8')

# Mapping German column names to English
column_mapping = {
    "Organisation": "Organization",
    "Steuerbegünstigte Zwecke": "Tax-Exempt Purposes",
    "Postleitzahl": "Postal Code",
    "Ort": "City",
    "Strasse": "Street",
    "Hausnummer": "House Number",
    "Hausnummerzusatz": "House Number Addition",
    "Postfach": "Post Box",
    "Staat": "Country",
    "Bundesland": "State",
    "Finanzamt": "Tax Office",
    "Datum der Erteilung Feststellungsbescheid": "Date of Determination Notice",
    "Datum der Erteilung Freistellungsbescheid": "Date of Exemption Notice",
    "Datum der Anerkennung als Partei/Wählervereinigung": "Date of Recognition as Party/Electoral Association",
    "Status als juristische Person": "Status as Legal Entity"
}

# Rename columns using the mapping
df.rename(columns=column_mapping, inplace=True)

# Drop columns starting from 'Tax Office' onward
columns_to_drop = df.columns[df.columns.get_loc("Tax Office"):].tolist()
df.drop(columns=columns_to_drop, inplace=True)

# Initialize translator
translator = GoogleTranslator(source='de', target='en')

# Function for translating a chunk of the column
def translate_chunk(text_chunk):
    return [translator.translate(str(text)) if pd.notnull(text) else text for text in text_chunk]

# Split the "Tax-Exempt Purposes" column into chunks to parallelize the translation process
chunk_size = 10000  # You can adjust this size based on your machine's performance
tax_exempt_column = df['Tax-Exempt Purposes']

# Split the column into chunks for parallel processing
chunks = [tax_exempt_column[i:i + chunk_size] for i in range(0, len(tax_exempt_column), chunk_size)]

# Use concurrent.futures to translate the chunks in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Map the translate_chunk function to the chunks
    results = list(executor.map(translate_chunk, chunks))

# Flatten the results back into the dataframe
df['Tax-Exempt Purposes'] = [item for sublist in results for item in sublist]

# Display the updated dataframe (first 5 rows)
print("\nUpdated DataFrame:")
print(df.head())

# Save the updated DataFrame to a new file
df.to_csv('updated_file.csv', index=False)
