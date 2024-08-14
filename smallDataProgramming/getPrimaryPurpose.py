import requests
import pandas as pd

target = "https://clinicaltrials.gov/api/v2/studies/NCT00339079"
response = requests.get(url=target)

data=response.json()

design_module = data.get('protocolSection', {}).get('designModule', {})
primary_purpose = design_module.get('designInfo', {}).get('primaryPurpose', {})
phase = design_module.get("phases", {})
phase = ' ,'.join([str(elem) for elem in phase])

print(phase)
# if primary_purpose == "TREATMENT":
#     nct_id = data.get('protocolSection', {}).get('identificationModule', {}).get('nctId', None)
#     print(nct_id)