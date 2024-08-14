import pandas as pd
import ast

df = pd.read_csv('combined_Dump_noResult.csv')  # Replace with your actual file path

# Define a function to check if 'cancer' is in a list of strings
def has_cancer_in_list(conditions_list):
    if isinstance(conditions_list, str): 
        try:
            conditions_list = ast.literal_eval(conditions_list)  
        except ValueError:
            return False  
    if isinstance(conditions_list, list):
        return any('cancer' in condition.lower() for condition in conditions_list)
    return False

def has_cancer_in_dict_list(meshes_list):
    if isinstance(meshes_list, str):
        try:
            meshes_list = ast.literal_eval(meshes_list) 
        except ValueError:
            return False  
    if isinstance(meshes_list, list):
        return any('cancer' in mesh['term'].lower() for mesh in meshes_list if isinstance(mesh, dict) and 'term' in mesh)
    return False

# Apply these functions to filter the DataFrame
filtered_df = df[df['protocolSection.conditionsModule.conditions'].apply(has_cancer_in_list) | 
                 df['derivedSection.conditionBrowseModule.meshes'].apply(has_cancer_in_dict_list)]

filtered_df.to_csv('Cancer_Dump_noResult.csv', index=False)
print("Filtered data saved to 'Cancer_Dump_noResult.csv'.")
