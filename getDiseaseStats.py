import pandas as pd

df = pd.read_csv('Prototype/Disease_Drug_trials_Parallel.csv')  # Make sure to adjust the file path
disease_counts = df['Disease Name'].value_counts()

total_entries = len(df)
disease_frequencies = disease_counts / total_entries

results_df = pd.DataFrame({
    'Count': disease_counts,
    'Frequency': (disease_frequencies*100).round(3)
})

print(results_df)
results_df.to_csv('Disease_Name_Counts_and_Frequencies.csv', index=True, index_label='Disease Name')
print("Results have been saved to Disease_Name_Counts_and_Frequencies.csv.")
