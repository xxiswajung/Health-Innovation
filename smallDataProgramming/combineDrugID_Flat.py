import pandas as pd
from datetime import datetime

print("Start time:", datetime.now().time())

# Load the first CSV file (the main data file with NCT numbers and other data)
main_csv_file_path = 'Output_Valid_SingleGroup.csv'  # Replace with the path to your main CSV file
main_df = pd.read_csv(main_csv_file_path)

# Load the second CSV file (the one containing NCT numbers and Drug IDs)
additional_csv_file_path = 'Drug_id_Drug_trials_SingleGroup.csv'  # Replace with the path to your additional CSV file
additional_df = pd.read_csv(additional_csv_file_path)

output_csv_path = 'Valid_SingleGroup_with_DrugId.csv'  # Replace with your desired output file path

main_df['NCT number'] = main_df['NCT number'].astype(str)
additional_df['NCT Number'] = additional_df['NCT Number'].astype(str)

merged_df = pd.merge(main_df, additional_df, left_on='NCT number', right_on='NCT Number', how='left')

# Optionally, drop the additional 'NCT Number' column from the merged DataFrame if it's redundant
merged_df.drop(columns=['NCT Number'], inplace=True)

# Assuming you want to keep all other columns from main_df as they are
column_order = ['NCT number', 'Drug ID'] + [col for col in merged_df.columns if col not in ['NCT number', 'Drug ID']]
merged_df = merged_df[column_order]

merged_df.to_csv(output_csv_path, index=False)

print("Merged data saved to:", output_csv_path)
print("End time:", datetime.now().time())
