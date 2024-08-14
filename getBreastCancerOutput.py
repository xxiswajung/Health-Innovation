import requests
import pandas as pd
from datetime import datetime
from decimal import Decimal
import re, ast

def safe_eval(data):
    if pd.isna(data) or not isinstance(data, str):
        return []
    try:
        return ast.literal_eval(data)
    except (ValueError, SyntaxError):
        return []


def categorize_string(s):
    patterns = {
        'PFS': r'progression[-\s]*free[-\s]*survival|pfs',
        'DFS': r'disease[-\s]*free[-\s]*survival|dfs',
        'OS': r'\boverall[-\s]*survival\b|\bos\b',
        'ORR': r'objective[-\s]*response[-\s]*rate|overall[-\s]*response[-\s]*rate|orr\b'
    }
    s = s.lower()
    for key, pattern in patterns.items():
        if re.search(pattern, s):
            return key
    return 

def is_numeric(value):
    try:
        float(value)  # Try converting the string to float
        return True
    except ValueError:
        return False  # If conversion fails, it's not a numeric string

def convert_to_list(data):
    if pd.isna(data):
        return []
    if isinstance(data, str):
        try:
            data = ast.literal_eval(data)
        except (ValueError, SyntaxError):
            return []
    return data


def extract_data(row, max_drug_count):
    efficacy_data_list = []

    # Extracting basic trial information
    nct_id = row['protocolSection.identificationModule.nctId']
    allocation = row['protocolSection.designModule.designInfo.allocation']
    masking = row['protocolSection.designModule.designInfo.maskingInfo.masking']
    model = row['protocolSection.designModule.designInfo.interventionModel']
    phases = convert_to_list(row['protocolSection.designModule.phases'])
    phase = ','.join(phases)

    parsed_groups = safe_eval(row['resultsSection.participantFlowModule.groups'])
    drug_names = [item['title'] for item in parsed_groups]    
    drug_names.extend([None] * (max_drug_count - len(drug_names)))

    placebo_index = next((i for i, name in enumerate(drug_names) if name and 'placebo' in name.lower()), None)
    side_effects = safe_eval(row['resultsSection.adverseEventsModule.eventGroups'])
    serious_adverse_events = next((item.get('seriousNumAffected') for item in side_effects), None)
    
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

    measuretitle_counters = {}
    measuretitle_counters=1

    outcome_measures = safe_eval(row['resultsSection.outcomeMeasuresModule.outcomeMeasures'])

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
    efficacy_data_list.append(efficacy_data)
    return efficacy_data_list

df = pd.read_csv('BreastCancer_addDummyColumn.csv')  # Replace with your actual file path
df = df[(df['breast_cancer_dummy'] == 1) & (df['hasResults'] == True)]
df['Parsed Groups'] = df['resultsSection.participantFlowModule.groups'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
max_drug_count = df['Parsed Groups'].apply(lambda x: len(x) if isinstance(x, list) else 0).max()
df['Efficacy Data'] = df.apply(lambda row: extract_data(row, max_drug_count), axis=1)
all_outcomes = pd.DataFrame([item for sublist in df['Efficacy Data'] for item in sublist])
csv_filename = "BreastCancer_Output_hasResult_v2.csv"
all_outcomes.to_csv(csv_filename, index=False)
print(f"All data saved to {csv_filename}")