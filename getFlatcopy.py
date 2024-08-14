import requests
import pandas as pd
from datetime import datetime
from decimal import Decimal
import re

def categorize_string(s):
    pfs_pattern = r'progression[-\s]*free[-\s]*survival|pfs'
    dfs_pattern = r'disease[-\s]*free[-\s]*survival|dfs'
    os_pattern = r'\boverall[-\s]*survival\b|\bos\b'
    orr_pattern = r'objective[-\s]*response[-\s]*rate|overall[-\s]*response[-\s]*rate|orr\b'
    
    lower_s = s.lower()
    
    if re.search(pfs_pattern, lower_s):
        return "PFS"
    elif re.search(dfs_pattern, lower_s):
        return "DFS"
    elif re.search(os_pattern, lower_s):
        return "OS"
    elif re.search(orr_pattern, lower_s):
        return "ORR"
    else:
        return None 

def is_numeric(value):
    try:
        float(value)  # Try converting the string to float
        return True
    except ValueError:
        return False  # If conversion fails, it's not a numeric string

def get_max_drug_count(lines):
    max_drug_count = 0
    for line in lines:
        target = "https://clinicaltrials.gov/api/v2/studies/" + line
        response = requests.get(url=target)
        data = response.json()
        arm_groups = data.get("resultsSection", {}).get("participantFlowModule", {}).get("groups", [])
        drug_names = [item.get("title") for item in arm_groups]         
        max_drug_count = max(max_drug_count, len(drug_names))
    return max_drug_count


def extract_data(data, max_drug_count):
    # Extracting basic trial information
    nct_id = data.get("protocolSection", {}).get("identificationModule", {}).get("nctId", None)
    allocation = data.get("protocolSection", {}).get("designModule", {}).get("designInfo", {}).get("allocation", None)
    masking = data.get("protocolSection", {}).get("designModule", {}).get("designInfo", {}).get("maskingInfo", {}).get("masking", None)
    model = data.get("protocolSection", {}).get("designModule", {}).get("designInfo", {}).get("interventionModel", None)
    phase = data.get("protocolSection", {}).get("designModule", {}).get("phases", None)
    if phase is not None:
        phase = ','.join([str(elem) for elem in phase])

    # # Extracting drug name
    # interventions = data.get("protocolSection", {}).get("armsInterventionsModule", {}).get("interventions", [])
    # drug_name = next((item.get("name") for item in interventions if item.get("name") != "Placebo"), None)
    arm_groups = data.get("resultsSection", {}).get("participantFlowModule", {}).get("groups", [])
    drug_names = [item.get("title") for item in arm_groups]
    drug_names.extend([None] * (max_drug_count - len(drug_names)))

    # Check if 'Placebo' is one of the drug names and store its index
    placebo_index = None
    for i, drug_name in enumerate(drug_names):
        if drug_name is not None:
            if 'placebo' in drug_name or 'Placebo' in drug_name:
                placebo_index = i + 1 

    # Extracting side effect data
    side_effects = data.get("resultsSection", {}).get("adverseEventsModule", {}).get("eventGroups", [])
    serious_adverse_events = next((item.get("seriousNumAffected") for item in side_effects), None)

    # Processing outcome measures
    outcome_measures = data.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])
    
    efficacy_data = {
        'NCT number': nct_id,
        'Allocation': allocation,
        'Masking': masking,
        'serious Adverse Events': serious_adverse_events,
        'Interventional Model': model,
        'Phase': phase
    }
    for i, drug_name in enumerate(drug_names, start=1):
        efficacy_data[f'Drug Name {i}'] = drug_name
    # Initialize counters for each phase
    measuretitle_counters = {}
    # for outcome in outcome_measures:
    #     groups=outcome.get("groups", [])
    #     for i, drug_name in enumerate(groups, start=1):
    #         efficacy_data[f'Drug Name {i}'] = drug_name.get("title", {})

    measuretitle_counters=1
    # Extracting efficacy data for each outcome measure
    for outcome in outcome_measures:
        OutcomeMeasureType = outcome.get("type", "")
        if OutcomeMeasureType == "PRIMARY":
            MT = categorize_string(outcome.get("title", ""))
            UM = outcome.get("unitOfMeasure", "").lower().strip()
            if (MT in ['OS', 'PFS'] and 'months' in UM) or (MT in ['ORR', 'DFS'] and 'percentage of participants' in UM):
                classes = outcome.get("classes", [])
                for clas in classes:
                    categories = clas.get("categories", [])
                    for category in categories:
                        measurements = category.get("measurements", [])
                        tmp=[]
                        for j, measurement in enumerate(measurements):
                            value_str = measurement.get("value", 0)
                            value = Decimal(value_str) if is_numeric(value_str) else value_str
                            drug_index = j % len(drug_names) + 1  # Zero-based index, incremented for display
                            efficacy_data[f'Drug_{drug_index}_{MT}{measuretitle_counters}_Value'] = value
                            tmp.append(value)

                        # Validate placebo_index before use
                        if placebo_index and placebo_index - 1 < len(tmp):
                            placebo_value = tmp[placebo_index - 1]

                            for k, value in enumerate(tmp, start=1):
                                if k != placebo_index:  # Skip placebo itself
                                    difference_key = f'Differences_{MT}{measuretitle_counters}_with_Drug{k}_and_Placebo'
                                    if isinstance(value, Decimal) and isinstance(placebo_value, Decimal):
                                        efficacy_data[difference_key] = value - placebo_value
                                    # else:
                                    #     efficacy_data[difference_key] = 'NA'

                        else:
                            # When no valid placebo index, calculate differences between Drug1 and others
                            if tmp and isinstance(tmp[0], Decimal):
                                drug1_value = tmp[0]
                                for k, other_value in enumerate(tmp[1:], start=2):
                                    if isinstance(other_value, Decimal):
                                        efficacy_data[f'Differences_{MT}{measuretitle_counters}_with_Drug1_and_Drug{k}'] = drug1_value - other_value
                                    # else:
                                    #     efficacy_data[f'Differences_{MT}{measuretitle_counters}_with_Drug1_and_Drug{k}'] = 'NA'

                measuretitle_counters += 1
    return efficacy_data

all_efficacy_data = []  # List to store all efficacy data


with open('Breast_NCT_Numbers.txt', 'r') as f: #397
    print("Start to count maximum number of drug:", datetime.now().time())
    lines = f.readlines()
    max_drug_count = 25
    print("Maximum number of drug:", max_drug_count)
    print("Finish to count maximum number of drug:", datetime.now().time())
    print("Start time:", datetime.now().time())
    

    for line in lines:
        line = line.strip()
        target = "https://clinicaltrials.gov/api/v2/studies/" + line
        response = requests.get(url=target)
        data = response.json()
        # Process and append the data
        processed_data = extract_data(data, max_drug_count)
        all_efficacy_data.append(processed_data)

df = pd.DataFrame(all_efficacy_data)
csv_filename = "Breast_Output_Valid_Parallel_v4.csv"
df.to_csv(csv_filename, index=False)

print("End time:", datetime.now().time())
print(f"All data saved to {csv_filename}")

