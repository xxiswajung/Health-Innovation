import requests
import pandas as pd
from datetime import datetime

def process_batch(batch, batch_index):
    all_efficacy_data = []
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=20)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    batch_filename = f"Dump_noResult_{batch_index}.csv"

    for nct_number in batch:
        target = f"https://clinicaltrials.gov/api/v2/studies/{nct_number}"
        try:
            response = session.get(url=target)
            response.raise_for_status()
            data = response.json()
            flat_data = pd.json_normalize(data)
            all_efficacy_data.append(flat_data)
        except Exception as e:
            print(f"Error processing {nct_number}: {str(e)}")

    if all_efficacy_data:
        df = pd.concat(all_efficacy_data, ignore_index=True)
        df.to_csv(batch_filename, index=False)
        print(f"Batch {batch_index} saved to {batch_filename}")

with open('noResult.txt', 'r') as file:
    lines = file.read().splitlines()

batch_size = 62000
num_batches = len(lines) // batch_size + (1 if len(lines) % batch_size != 0 else 0)

print("Start processing:", datetime.now().time())

# Process each batch
for i in range(num_batches):
    start_index = i * batch_size
    end_index = start_index + batch_size
    batch = lines[start_index:end_index]
    print(f"Processing batch {i+1}/{num_batches}, Start time:", datetime.now().time())
    process_batch(batch, i+1)

print("End processing:", datetime.now().time())
