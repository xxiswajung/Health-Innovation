import requests
import pandas as pd
from datetime import datetime

print("Start time:", datetime.now().time())

df = pd.read_csv('Valid_SingleGroup_with_DrugId_and_Disease.csv')
bf = pd.read_csv('Disease_Drug_trials_SingleGroup.csv')

unique_disease_names = bf['Disease Name'].unique()
top_dispersion_types = {}

for name in unique_disease_names:
    disease_df = df[df['Disease Name'] == name]
    nct_numbers = disease_df['NCT number']
    cumulative_dispersion_count = {}

    for nct_number in nct_numbers:
        target = f"https://clinicaltrials.gov/api/v2/studies/{nct_number}"
        try:
            response = requests.get(url=target)
            response.raise_for_status()  
            data = response.json()
            other_events = data.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])

            for outcome in other_events:
                dispersion_type = outcome.get("dispersionType", "")
                if dispersion_type:  
                    cumulative_dispersion_count[dispersion_type] = cumulative_dispersion_count.get(dispersion_type, 0) + 1
        
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred for NCT Number {nct_number}: {err}")
        except requests.exceptions.RequestException as err:
            print(f"Request error occurred for NCT Number {nct_number}: {err}")
        except ValueError as err:
            print(f"JSON decoding failed for NCT Number {nct_number}: {err}")

    # Sort and get top 3 dispersion types
    sorted_dispersion_types = sorted(cumulative_dispersion_count.items(), key=lambda item: item[1], reverse=True)[:3]
    top_dispersion_types[name] = sorted_dispersion_types

records = []
for disease, disp_types in top_dispersion_types.items():
    record = {'Disease Name': disease}
    for i, (disp_type, count) in enumerate(disp_types, 1):
        record[f'Top {i} Dispersion Type'] = disp_type
        # record[f'Top {i} Count'] = count
    records.append(record)

results_df = pd.DataFrame(records)
results_df.to_csv('Top_Dispersion_Types_Per_Disease_SingleGroup.csv', index=False)
print("End time:", datetime.now().time())
print("Top dispersion types per disease have been saved to Top_Dispersion_Types_Per_Disease.csv.")
