import requests
from datetime import datetime

source_file_path = './NCTnumber/SingleGroup.txt'  
destination_file_path_1 = './NCTnumber/NA_SingleGroup.txt'  
destination_file_path_2 = './NCTnumber/Valid_SingleGroup.txt'  

def extract_data(data, NA_nct, Valid_nct):
    nct_id = data.get("protocolSection", {}).get("identificationModule", {}).get("nctId", None)
    if nct_id:
        has_valid_data = False
        outcome_measures = data.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])
        for outcome in outcome_measures:
            classes = outcome.get("classes", [])
            for clas in classes:
                categories = clas.get("categories", [])
                for category in categories:
                    measurements = category.get("measurements", [])
                    if measurements:
                        has_valid_data = True
                        break
            if has_valid_data:
                break
        
        if has_valid_data:
            Valid_nct.add(nct_id)
        else:
            NA_nct.add(nct_id)

with open(source_file_path, 'r') as f:
    lines = f.readlines()
    print("Start time:", datetime.now().time())
    NA_nct = set()
    Valid_nct = set()
    for line in lines:
        line = line.strip()

        target = "https://clinicaltrials.gov/api/v2/studies/" + line
        response = requests.get(url=target)
        data = response.json()

        extract_data(data, NA_nct, Valid_nct)

print("The number of NA NCT is ", len(NA_nct))
print("The numer of Valid NCT is ", len(Valid_nct))

NA_list = sorted(list(NA_nct))
Valid_list = sorted(list(Valid_nct))

with open(destination_file_path_1, 'w') as f:
    for item in NA_list:
        f.write("%s\n" % item)

with open(destination_file_path_2, 'w') as f:
    for nct in Valid_list:
        f.write("%s\n" % nct)

print("End time:", datetime.now().time())
