import csv
import sys
import re
import pandas as pd
from datetime import datetime

csv.field_size_limit(sys.maxsize)

# 파일 경로 설정
filename = '../Raw Data/Drug_trials.csv'  # Replace with the path to your raw data CSV file
nctname = './NCTnumber/diff_validSingleGroup_DrugTrials.txt'  # Replace with the path to your NCT number file
main_csv_file_path = 'Prototype/Output_Valid_SingleGroup.csv'  # Replace with the path to your main CSV file
final_output_csv_path = 'TEST_Valid_SingleGroup_with_DrugId_and_Disease.csv'  # Final output file path

# 정규 표현식 패턴
drugId_pattern = re.compile(r'drugId:(\d+)')  # drugId: extract the drug ID
disease_pattern = re.compile(r"trialdiseasesID:(\d+);trialdiseasesNAME:([^;]+)")  # extract the very first disease's id and its name

drug_results = []  
disease_results = []  

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
                drug_results.append({
                    'NCT Number': nct_number,
                    'Drug ID': drug_id_match.group(1)  # extract the drug ID
                })
            disease_match = disease_pattern.search(row['trialTherapeuticAreas'])
            if disease_match:
                disease_results.append({
                    'NCT Number': nct_number,
                    'Disease ID': disease_match.group(1),  # extract the disease ID
                    'Disease Name': disease_match.group(2)  # extract the disease name
                })

drug_df = pd.DataFrame(drug_results)
disease_df = pd.DataFrame(disease_results)

# Sort the DataFrames by 'NCT Number' column
drug_df_sorted = drug_df.sort_values(by='NCT Number')
disease_df_sorted = disease_df.sort_values(by='NCT Number')

main_df = pd.read_csv(main_csv_file_path)
main_df['NCT number'] = main_df['NCT number'].astype(str)
drug_df_sorted['NCT Number'] = drug_df_sorted['NCT Number'].astype(str)
disease_df_sorted['NCT Number'] = disease_df_sorted['NCT Number'].astype(str)

merged_df_drug = pd.merge(main_df, drug_df_sorted, left_on='NCT number', right_on='NCT Number', how='left')
merged_df = pd.merge(merged_df_drug, disease_df_sorted, left_on='NCT number', right_on='NCT Number', how='left')

# Optionally, drop the additional 'NCT Number' columns from the merged DataFrame if they're redundant
merged_df.drop(columns=['NCT Number_x', 'NCT Number_y'], inplace=True)

# Rearrange the columns to make Drug ID and Disease ID appear right after NCT number
column_order = ['NCT number', 'Drug ID', 'Disease ID', 'Disease Name'] + [col for col in merged_df.columns if col not in ['NCT number', 'Drug ID', 'Disease ID', 'Disease Name']]
merged_df = merged_df[column_order]

# Save the final merged DataFrame to a new CSV file
merged_df.to_csv(final_output_csv_path, index=False)

print(f"Final merged data saved to: {final_output_csv_path}")
print("End time:", datetime.now().time())
