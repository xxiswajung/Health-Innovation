import pandas as pd
import ast

df = pd.read_csv('merged_Dump.csv')  # Replace with your actual file path
df = df[(df['protocolSection.designModule.designInfo.interventionModel'] == 'PARALLEL')]

# Function to process conditions and convert them from string to list if needed
def process_conditions(data):
    if pd.isna(data):
        return []
    if isinstance(data, str):
        try:
            data = ast.literal_eval(data)
        except (ValueError, SyntaxError):
            return []
    return data

# Function to check for 'breast cancer' in a list of strings or dictionaries
def has_breast_cancer(conditions_list, dict_list):
    if any('breast cancer' in condition.lower() for condition in conditions_list):
        return True
    if any('breast cancer' in mesh['term'].lower() for mesh in dict_list if 'term' in mesh):
        return True
    return False

# Apply the functions to check for breast cancer presence in each row
df['hasBreastCancer'] = df.apply(
    lambda row: has_breast_cancer(
        process_conditions(row['protocolSection.conditionsModule.conditions']),
        process_conditions(row['derivedSection.conditionBrowseModule.meshes'])
    ), axis=1)

# Create a new column for the dummy variable
df['breast_cancer_dummy'] = df['hasBreastCancer'].apply(lambda x: 1 if x else 0)
df.drop('hasBreastCancer', axis=1, inplace=True)

# Save the updated DataFrame to a new CSV file
new_csv_filename = 'BreastCancer_addDummyColumn.csv'
df.to_csv(new_csv_filename, index=False)

print(f"Data with 'breast_cancer_dummy' has been saved to {new_csv_filename}")
