import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('Valid_SingleGroup_with_DrugId_and_Disease.csv')  # Make sure to adjust the file path

# Drop rows where 'Disease Name' is empty or NaN
df = df.dropna(subset=['Disease Name'])

# Save the cleaned DataFrame back to a CSV file
df.to_csv('cleaned_Valid_SingleGroup_with_DrugId_and_Disease.csv', index=False)  # Adjust the output file name as needed

print("Cleaned data has been saved to cleaned_file.csv.")
