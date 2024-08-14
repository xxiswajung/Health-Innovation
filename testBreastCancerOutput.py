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

    # Safely evaluate and extract drug names
    parsed_groups = safe_eval(row['resultsSection.participantFlowModule.groups'])
    drug_names = [item['title'] for item in parsed_groups]
    drug_names.extend([None] * (max_drug_count - len(drug_names)))

    placebo_index = next((i for i, name in enumerate(drug_names) if name and 'placebo' in name.lower()), None)

    efficacy_data = {
        'NCT ID': nct_id,
        'Allocation': allocation,
        'Masking': masking,
        'Model': model,
        'Phase': phase,
        'Drug Names': drug_names,
        'Placebo Index': placebo_index
    }

    # Extract efficacy measures
    measures = safe_eval(row['resultsSection.outcomeMeasureModule.outcomeMeasures'])
    measuretitle_counters = 0
    for measure in measures:
        MT = categorize_string(measure['title'])
        if MT:
            for group in measure['groups']:
                key = f'{MT}{measuretitle_counters}_Drug{group["id"]}'
                value = group['value']
                if is_numeric(value):
                    efficacy_data[key] = Decimal(value)
                else:
                    efficacy_data[key] = value

            # Calculate differences with placebo if available
            if placebo_index is not None and len(parsed_groups) > placebo_index:
                placebo_value = Decimal(parsed_groups[placebo_index]['value'])
                for k, item in enumerate(parsed_groups):
                    if k != placebo_index:
                        difference_key = f'Differences_{MT}{measuretitle_counters}_with_Drug{k}_and_Placebo'
                        if isinstance(value, Decimal):
                            efficacy_data[difference_key] = value - placebo_value

            measuretitle_counters += 1

    efficacy_data_list.append(efficacy_data)
    return efficacy_data_list

# Reading the data and processing
df = pd.read_csv('BreastCancer_addDummyColumn.csv')
df['Parsed Groups'] = df['resultsSection.participantFlowModule.groups'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
max_drug_count = df['Parsed Groups'].apply(lambda x: len(x) if isinstance(x, list) else 0).max()
df['Efficacy Data'] = df.apply(lambda row: extract_data(row, max_drug_count), axis=1)
all_outcomes = pd.DataFrame([item for sublist in df['Efficacy Data'] for item in sublist])
csv_filename = "BreastCancer_Output.csv"
all_outcomes.to_csv(csv_filename, index=False)
print(f"All data saved to {csv_filename}")
