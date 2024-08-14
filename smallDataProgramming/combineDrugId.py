import csv, sys, re
import pandas as pd
from datetime import datetime

csv.field_size_limit(sys.maxsize)

filename = '../Raw Data/Drug_trials.csv'
nctname = './NCTnumber/diff_validSingleGroup_DrugTrials.txt'
output_file_name = 'Drug_id_Drug_trials_SingleGroup.csv'

# 정규 표현식 패턴
drugId_pattern = re.compile(r'drugId:(\d+)') 
results = []  
print("Start time:", datetime.now().time())

with open(nctname, 'r') as f:
    nct_numbers = [line.strip() for line in f.readlines()]

with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)

for nct_number in nct_numbers:
    for row in rows:
        if nct_number in row['trialProtocolIDs']:
            drug_id_match = drugId_pattern.search(row['trialPrimaryDrugsTested'])
            if drug_id_match:
                results.append({
                    'NCT Number': nct_number,
                    'Drug ID': drug_id_match.group()[7:]  # Extract the drug ID from the matched string
                    })

df = pd.DataFrame(results)

df_sorted = df.sort_values(by='NCT Number')
df_sorted.to_csv(output_file_name, index=False)

print(f"Completed writing to {output_file_name}.")
print("End time:", datetime.now().time())
