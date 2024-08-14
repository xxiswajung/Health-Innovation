import requests
import pandas as pd
from decimal import Decimal
import re

def categorize_string(s):
    pfs_pattern = r'progression[-\s]*free[-\s]*survival|pfs'
    dfs_pattern = r'disease[-\s]*free[-\s]*survival|dfs'
    os_pattern = r'\boverall[-\s]*survival\b|\bos\b'
    orr_pattern = r'objective[-\s]*response[-\s]*rate|overall[-\s]*response[-\s]*rate|orr\b'
    dor_pattern = r'duration[-\s]*of[-\s]*response|\bdor\b|\bdr\b'

    lower_s = s.lower()
    
    if re.search(pfs_pattern, lower_s):
        return "PFS"
    elif re.search(dfs_pattern, lower_s):
        return "DFS"
    elif re.search(os_pattern, lower_s):
        return "OS"
    elif re.search(orr_pattern, lower_s):
        return "ORR"
    elif re.search(dor_pattern, lower_s):
        return "DOR"
    else:
        return None  

def is_numeric(value):
    try:
        float(value)  
        return True
    except ValueError:
        return False  

df = pd.read_csv('Valid_Parallel_with_DrugId_and_Disease.csv')  

prostate_df = df[df['Disease Name'] == 'Breast']
prostate_nct_numbers = prostate_df['NCT number']

cumulative_measure_title_count = {}
measure_values = {}
unit_of_measure_count = {}
cumulative_unit_of_measure_title_count={}
nct=[]

for nct_number in prostate_nct_numbers:
    target = f"https://clinicaltrials.gov/api/v2/studies/{nct_number}"
    response = requests.get(url=target)
    data = response.json()

    other_events = data.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])
  
    for outcome in other_events:
        # Extract the 'title' field from the outcome measure
        outcomeMeasureType = outcome.get("type", "")
        if outcomeMeasureType == "SECONDARY":
            measure_title = outcome.get("title", "")
            if categorize_string(measure_title):  # Check if measure_title is not empty
            #     unit_of_measure = outcome.get("unitOfMeasure", "").lower()
            #     if unit_of_measure=='months':
            #         nct.append(nct_number)
            #     # if unit_of_measure:
            #         # if unit_of_measure in unit_of_measure_count:
            #         #     unit_of_measure_count[unit_of_measure] += 1
            #         # else:
            #         #     cumulative_unit_of_measure_title_count[unit_of_measure] = []
            #         #     unit_of_measure_count[unit_of_measure] = 1
                if categorize_string(measure_title) in cumulative_measure_title_count:
                    cumulative_measure_title_count[categorize_string(measure_title)] += 1
                else:
                    measure_values[categorize_string(measure_title)] = []
                    cumulative_measure_title_count[categorize_string(measure_title)] = 1
            else:
                if measure_title in cumulative_measure_title_count:
                    cumulative_measure_title_count[measure_title] += 1
                else:
                    measure_values[measure_title] = []
                    cumulative_measure_title_count[measure_title] = 1

            # Extracting the value of each outcome measure title   
#                 classes = outcome.get("classes", [])
#                 for clas in classes:
#                     categories = clas.get("categories", [])
#                     for category in categories:
#                         measurements = category.get("measurements", [])
#                         tmp=[]
#                         for j, measurement in enumerate(measurements):
#                             value_str=measurement.get("value",0)
#                             if is_numeric(value_str):
#                                 value = Decimal(value_str)
#                                 if categorize_string(measure_title):
#                                     cumulative_unit_of_measure_title_count[unit_of_measure].append(float(value))
#                                 else:
#                                     cumulative_unit_of_measure_title_count[unit_of_measure].append(float(value))
        
total_count = sum(cumulative_measure_title_count.values())
records = []

for title, values in cumulative_measure_title_count.items():
    count = cumulative_measure_title_count[title]
    percentage = (count / total_count) * 100  # Calculate percentage here
#     min_val = min(values) if values else None
#     max_val = max(values) if values else None
#     avg_val = sum(values) / len(values) if values else None
#     std_dev = pd.Series(values).std() if values else None  # Calculate standard deviation
    records.append({
        'Measure Title': title,
        'Count': count,
        'Percentage': round(percentage, 3),  # Round the percentage to three decimals
#         'Min': min_val,
#         'Max': max_val,
#         'Avg': avg_val,
#         'Std Dev': std_dev
    })

results_df = pd.DataFrame(records)
results_df = results_df.sort_values(by='Count', ascending=False)
results_df.reset_index(drop=True, inplace=True)

results_df.to_csv('Breast_Measure_Counts_Secondary.csv', index=False)
print("Cumulative data has been saved")