# import pandas as pd

# # Load the Excel file
# excel_file_path = 'ctg-studies.csv'  # Replace with the path to your Excel file
# df = pd.read_csv(excel_file_path)

# # Filter rows where 'Primary Purpose: TREATMENT' is in the 'Study Design' column
# filtered_df = df[df['Study Design'].str.contains('Primary Purpose: TREATMENT')].copy()

# # Extract 'Intervention Model' from the 'Study Design' column
# def extract_intervention_model(design):
#     parts = design.split('|')
#     model_part = [part for part in parts if 'Intervention Model:' in part]
#     if model_part:
#         return model_part[0].split(': ')[1].strip()
#     else:
#         return None

# filtered_df['Intervention Model'] = filtered_df['Study Design'].apply(extract_intervention_model)

# parallel_df = filtered_df[filtered_df['Intervention Model'] == '']
# final_df = parallel_df[['NCT Number', 'Intervention Model']]

# # Sort the DataFrame by 'NCT Number' in ascending order
# final_output_sorted = final_df.sort_values(by='NCT Number', ascending=True)

# # Save the result to a new Excel file
# output_file_path = 'NoInterventional.csv'  # Replace with the path where you want to save the output file
# final_output_sorted.to_csv(output_file_path, index=False)

# print(f"Data saved to {output_file_path}")

# import pandas as pd

# df = pd.read_csv('ctg-studies_noresult.csv')  # Adjust the path to your actual file

# # Define a function to extract the intervention model
# def extract_intervention_model(design):
#     if not isinstance(design, str):
#         return None
#     parts = design.split('|')
#     for part in parts:
#         if 'Intervention Model:' in part:
#             return part.split(':', 1)[1].strip()
#     return None  

# # Apply the function to each row in the 'Study Design' column
# df['Intervention Model'] = df['Study Design'].apply(extract_intervention_model)

# # Save the DataFrame back to CSV
# df.to_csv('updated_file_noresult.csv', index=False)

# import requests
# import pandas as pd

# target = "https://clinicaltrials.gov/api/v2/studies/NCT00220779"
# response = requests.get(url=target)

# data=response.json()
# conditions = data.get("protocolSection", {}).get("conditionsModule", {}).get("conditions", [])
# for condition in conditions:
#     print(condition)

import pandas as pd
from collections import Counter
import re

def count_conditions(df, column_name='Conditions'):
    word_count = Counter()
    
    for entry in df[column_name]:
        if pd.notna(entry):  
            # Normalize the entry to lower case and replace | with ,
            normalized_entry = re.sub(r'\s*\|\s*', ', ', entry.lower())
            conditions = [word.strip() for word in normalized_entry.split(',')]
            word_count.update(conditions)
    
    return word_count

df = pd.read_csv('ctg-studies_diseaseorcondition.csv')  # Adjust the path to your actual file
conditions_count = count_conditions(df, 'Conditions')

conditions_df = pd.DataFrame(list(conditions_count.items()), columns=['Disease or Condition', 'Count'])
total_count = conditions_df['Count'].sum()

conditions_df['Percentage'] = (conditions_df['Count'] / total_count * 100).round(6)
conditions_df = conditions_df.sort_values(by='Count', ascending=False)

conditions_df.to_csv('DiseaseOrCondition.csv', index=False)

print("Condition counts saved.")
