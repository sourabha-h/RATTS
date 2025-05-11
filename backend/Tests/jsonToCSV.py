
from pandas import json_normalize
import json
import os

## Function to convert json template to csv ##
def jsonToCSV(json_file,csv_file):
    with open(json_file) as data_file:    
        d= json.load(data_file)  
    df = json_normalize(d)
    df.head(0).to_csv(csv_file, index=False)

## Calling ##
for root, dirs, files in os.walk("templates"):
    for file in files:
        if file.startswith("rest") and file.endswith(".template"):
             jsonToCSV(os.path.join(root, file),os.path.join("csvfiles", file.removeprefix("rest").removesuffix(".template")+".csv"))
