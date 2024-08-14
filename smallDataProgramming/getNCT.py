import pandas as pd

df = pd.read_csv('ctg-studies_noresult.csv') 

sorted_nct_numbers = df['NCT Number'].sort_values().dropna()

print(len(sorted_nct_numbers))
with open('noResult.txt', 'w') as f:
    for number in sorted_nct_numbers:
        f.write(str(number) + '\n')

print("Sorted NCT numbers have been saved to 'noResult.txt'")
