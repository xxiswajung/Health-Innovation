import pandas as pd
from collections import Counter

# Load the CSV file
df = pd.read_csv('Merged_Dump.csv')

# 리드 스폰서의 빈도를 계산
sponsor_counts = Counter(df['protocolSection.identificationModule.organization.fullName'].dropna())

# Convert the counter to a DataFrame for better visualization and further processing
sponsor_counts_df = pd.DataFrame(sponsor_counts.items(), columns=['Organization', 'Count'])
total_sponsors = sum(sponsor_counts.values())
sponsor_counts_df['Frequency (%)'] = (sponsor_counts_df['Count'] / total_sponsors * 100).round(3)

# Sort the DataFrame by count in descending order
sponsor_counts_df.sort_values('Count', ascending=False, inplace=True)

# Save the result to a CSV file
sponsor_counts_df.to_csv('Organization_counts.csv', index=False)
print("LeadSponsor counts saved to 'Organization_counts.csv'.")

#  import pandas as pd
# from collections import Counter
# import ast

# def process_phases(data):
#     if pd.isna(data):
#         return []
#     if isinstance(data, str):
#         try:
#             # Assuming the data is stored as a string representation of a list
#             data = ast.literal_eval(data)
#         except (ValueError, SyntaxError):  # Handling both ValueError and SyntaxError
#             return []  # Return an empty list if the data cannot be parsed
#     return data

# # Load the CSV file
# df = pd.read_csv('Merged_Dump.csv')
# phase_counts = Counter()

# # Count the frequency of each phase
# for phases in df['protocolSection.sponsorCollaboratorsModule.leadSponsor.name']:
#     phase_list = process_phases(phases)
#     phase_counts.update(phase_list)

# # Convert the counter to a DataFrame for better visualization and further processing
# phase_counts_df = pd.DataFrame(phase_counts.items(), columns=['leadSponsor', 'Count'])
# total_phases = sum(phase_counts.values())
# phase_counts_df['Frequency (%)'] = (phase_counts_df['Count'] / total_phases * 100).round(3)

# # Sort the DataFrame by count in descending order
# phase_counts_df.sort_values('Count', ascending=False, inplace=True)

# # Save the result to a CSV file
# phase_counts_df.to_csv('leadSponsor_counts.csv', index=False)
# print("Phase counts saved to 'leadSponsor_counts.csv'.")

# import pandas as pd
# from collections import Counter
# import ast

# def process_conditions(data):
#     if pd.isna(data):
#         return []
#     if isinstance(data, str):
#         try:
#             # Assuming the data is stored as a string representation of a list
#             data = ast.literal_eval(data)
#         except ValueError:
#             return []  # Return an empty list if the data cannot be parsed
#     return data

# # Load the CSV file
# df = pd.read_csv('Cancer_Dump_noResult.csv')
# condition_counts = Counter()

# for conditions in df['protocolSection.conditionsModule.conditions']:
#     condition_list = process_conditions(conditions)
#     condition_counts.update(condition_list)

# # Convert the counter to a DataFrame for better visualization and further processing
# condition_counts_df = pd.DataFrame(condition_counts.items(), columns=['Condition', 'Count'])
# total_conditions = sum(condition_counts.values())
# condition_counts_df['Frequency (%)'] = (condition_counts_df['Count'] / total_conditions * 100).round(3)

# condition_counts_df.sort_values('Count', ascending=False, inplace=True)
# condition_counts_df.to_csv('condition_counts_Cancer_Dump_noResult.csv', index=False)
# print("Condition counts saved to 'condition_counts_Cancer_Dump_validResult.csv'.")
# import pandas as pd
# from collections import Counter
# import ast

# def has_cancer_in_dict_list(meshes_list):
#     if isinstance(meshes_list, str):
#         try:
#             meshes_list = ast.literal_eval(meshes_list) 
#         except ValueError:
#             return False  
#     if isinstance(meshes_list, list):
#         return any('cancer' in mesh['term'].lower() for mesh in meshes_list if isinstance(mesh, dict) and 'term' in mesh)
#     return False

# # Load the CSV file
# df = pd.read_csv('Cancer_Dump_validResult.csv')

# # Apply the function to filter rows where the meshes list contains 'cancer'
# df_cancer = df[df['derivedSection.conditionBrowseModule.meshes'].apply(has_cancer_in_dict_list)]

# # Initialize a counter to store condition counts
# condition_counts = Counter()

# # Count occurrences of 'cancer' condition
# for index, row in df_cancer.iterrows():
#     # Extract the meshes list directly
#     meshes_list = row['derivedSection.conditionBrowseModule.meshes']
#     if isinstance(meshes_list, str):
#         try:
#             meshes_list = ast.literal_eval(meshes_list)
#         except ValueError:
#             continue
#     if isinstance(meshes_list, list):
#         for mesh in meshes_list:
#             if 'term' in mesh and 'cancer' in mesh['term'].lower():
#                 condition_counts.update([mesh['term'].lower()])
# # Convert the counter to a DataFrame
# condition_counts_df = pd.DataFrame(list(condition_counts.items()), columns=['Condition', 'Count'])

# # Calculate the total count of 'cancer' conditions
# total_conditions = sum(condition_counts.values())

# # Calculate the frequency (percentage) of 'cancer'
# condition_counts_df['Frequency (%)'] = (condition_counts_df['Count'] / total_conditions * 100).round(3)

# # Sort the DataFrame by count in descending order
# condition_counts_df.sort_values('Count', ascending=False, inplace=True)

# # Save the DataFrame to a new CSV file
# condition_counts_df.to_csv('condition_counts_Cancer_Dump_validResult2.csv', index=False)

# print("Cancer condition counts and frequencies saved to 'condition_counts_Cancer_Dump_validResult2.csv'.")
