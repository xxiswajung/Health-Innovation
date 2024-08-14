import requests
import pandas as pd

bf = pd.read_csv('Disease_Drug_trials_Parallel.csv')  # Adjust the file path as needed
# Load the CSV file into a DataFrame
df = pd.read_csv('Valid_Parallel_with_DrugId_and_Disease.csv')  # Adjust the file path as needed

# Extract unique disease names
unique_disease_names = bf['Disease Name'].unique()

for name in unique_disease_names:
    print(name)
    # Filter the DataFrame for rows where the 'Disease Name' is 'Prostate'
    prostate_df = df[df['Disease Name'] == name]

    # Extract the 'NCT number' column from the filtered DataFrame
    prostate_nct_numbers = prostate_df['NCT number']

    # Initialize a dictionary to track cumulative dispersion types
    cumulative_dispersion_count = {}

    # Iterate over each NCT number
    for nct_number in prostate_nct_numbers:
        target = f"https://clinicaltrials.gov/api/v2/studies/{nct_number}"
        response = requests.get(url=target)
        data = response.json()

        # Extract data from JSON response
        other_events = data.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])
        
        for outcome in other_events:
            dispersion_type = outcome.get("dispersionType", "")
            if dispersion_type:  # Check if dispersionType is not empty
                if dispersion_type in cumulative_dispersion_count:
                    cumulative_dispersion_count[dispersion_type] += 1
                else:
                    cumulative_dispersion_count[dispersion_type] = 1

    # Create a DataFrame from the cumulative dispersion count dictionary
    results_df = pd.DataFrame(list(cumulative_dispersion_count.items()), columns=['Dispersion Type', 'Count'])

    # Save the DataFrame to a CSV file
    results_df.to_csv('Cumulative_Dispersion_Type_Counts.csv', index=False)
    print("Cumulative data has been saved to Cumulative_Dispersion_Type_Counts.csv.")


