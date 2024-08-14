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

def count_metric_occurrences(outcomes, metric):
    count = 0
    for outcome in outcomes:
        if categorize_string(outcome) == metric:
            count += 1
    return count

def extract_data(row):
    efficacy_data_list = []

    # Extracting basic trial information
    nct_id = row['protocolSection.identificationModule.nctId']
    efficacy_data = {
        'NCT number': nct_id,
    }
    # Initialize the counts for primary and secondary metrics
    # primary_counts = {'PFS': 0, 'DFS': 0, 'OS': 0, 'ORR': 0}
    # secondary_counts = {'PFS': 0, 'DFS': 0, 'OS': 0, 'ORR': 0}
    primary_counts = 0
    secondary_counts = 0
    outcome_measures = safe_eval(row['resultsSection.outcomeMeasuresModule.outcomeMeasures'])

    # Extracting efficacy data for each outcome measure
    for outcome in outcome_measures:
        OutcomeMeasureType = outcome.get("type", "")
        MT = categorize_string(outcome.get("title", ""))
        UM = outcome.get("unitOfMeasure", "").lower().strip()
        
        if OutcomeMeasureType == "PRIMARY":
            primary_counts+=1
        elif OutcomeMeasureType == "SECONDARY":
            secondary_counts+=1
    #     if MT in ['OS', 'PFS', 'ORR', 'DFS']:
    #         if OutcomeMeasureType == "PRIMARY":
    #             if (MT in ['OS', 'PFS'] and 'months' in UM) or (MT in ['ORR', 'DFS'] and 'percentage of participants' in UM):
    #                 primary_counts[MT] += 1
    #         elif OutcomeMeasureType == "SECONDARY":
    #             if (MT in ['OS', 'PFS'] and 'months' in UM) or (MT in ['ORR', 'DFS'] and 'percentage of participants' in UM):
    #                 secondary_counts[MT] += 1
    # efficacy_data.update({
    #     'PFS_Primary_dummy': primary_counts['PFS'],
    #     'PFS_Secondary_dummy': secondary_counts['PFS'],
    #     'DFS_Primary_dummy': primary_counts['DFS'],
    #     'DFS_Secondary_dummy': secondary_counts['DFS'],
    #     'OS_Primary_dummy': primary_counts['OS'],
    #     'OS_Secondary_dummy': secondary_counts['OS'],
    #     'ORR_Primary_dummy': primary_counts['ORR'],
    #     'ORR_Secondary_dummy': secondary_counts['ORR']
    # })
    efficacy_data.update({
        'Primary_Count_dummy': primary_counts,
        'Secondary_Count_dummy': secondary_counts
    })
    efficacy_data_list.append(efficacy_data)
    return efficacy_data_list

df = pd.read_csv('BreastCancer_addDummyColumn.csv')  # Replace with your actual file path
df = df[(df['breast_cancer_dummy'] == 1)]
# df['Parsed Groups'] = df['resultsSection.participantFlowModule.groups'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
# max_drug_count = df['Parsed Groups'].apply(lambda x: len(x) if isinstance(x, list) else 0).max()
df['Efficacy Data'] = df.apply(lambda row: extract_data(row), axis=1)
all_outcomes = pd.DataFrame([item for sublist in df['Efficacy Data'] for item in sublist])
csv_filename = "BreastCancer_addCountColumns_Primary_Secondary.csv"
all_outcomes.to_csv(csv_filename, index=False)
print(f"All data saved to {csv_filename}")