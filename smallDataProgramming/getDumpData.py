import requests
import pandas as pd
from datetime import datetime
import random

with open('noResult.txt', 'r') as f:
    lines = f.read().splitlines()

# selected_lines = random.sample(lines, 100)
selected_lines = ['NCT01164189','NCT05393453']
all_efficacy_data = []

for nct_number in selected_lines:
    target = f"https://clinicaltrials.gov/api/v2/studies/{nct_number}"
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries = 20)
    sess.mount('http://', adapter)
    sess.mount('https://', adapter)
    try:
        response = sess.get(url=target)
        response.raise_for_status() 
        data = response.json()
        flat_data = pd.json_normalize(data)
        all_efficacy_data.append(flat_data)
    except requests.exceptions.HTTPError as errh:
        print(nct_number)
        print("End time:", datetime.now().time())
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(nct_number)
        print("End time:", datetime.now().time())
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(nct_number)
        print("End time:", datetime.now().time())
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(nct_number)
        print("End time:", datetime.now().time())
        print(f"OOps: Something Else: {err}")


df = pd.concat(all_efficacy_data, ignore_index=True)
csv_filename = "noResult_NCT01164189NCT05393453.csv"
df.to_csv(csv_filename, index=False)
# print(f"Data saved to {csv_filename}")
ef = pd.read_csv(csv_filename)  # Replace with your actual file path

# Count the number of columns in the DataFrame
number_of_columns = len(ef.columns)

print("Number of columns in the CSV file:", number_of_columns)