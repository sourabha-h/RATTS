# import pyyaml module
import yaml
from yaml.loader import SafeLoader
import re
import csv
#from Tests.flist_validation import flist_validation
from pathlib import Path
import argparse
from pandas import json_normalize
import json
import os

def create_csv(templatename,foldername):
    
    
    opcode_name=templatename[0:templatename.find('.')]
    csvfilename=opcode_name+"_template.csv"

    # Open the file and load the file
    with open("Data/Templates/"+foldername+"/"+templatename,'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    
    #dataarr=data[data.find('${')+2:data.find('}')]
    pat = r'(?<=\{).+?(?=\})'
    dataarr=re.findall(pat,data)
    dataarr.insert(0,'no')
    dataarr.insert(1,'testcase')
    
    if foldername.endswith("templates"):
        system_name = foldername[:foldername.rfind("templates")].rstrip("/")

    with open('Data/csvfiles/'+system_name+"/"+csvfilename,'w') as f:
        opobj=csv.writer(f)
        opobj.writerow(dataarr)
    
## Function to convert json template to csv ##
def jsonToCSV(json_file,csv_file):
    with open(json_file) as data_file:    
        d= json.load(data_file)  
    df = json_normalize(d)
    df.head(0).to_csv(csv_file, index=False)

"""
#filename='cusopsearch.yaml.template'
#filename='cusopcustvalidatechangeplan.yaml.template'
parser = argparse.ArgumentParser(description='Script so useful.')
parser.add_argument("--mode")

args = parser.parse_args()

mode_value = args.mode
#print(mode_value)
if(mode_value == 'soap'):
    folderpath = Path("Data/Templates/soaptemplates")
    foldername='soaptemplates'
    filelist=list(folderpath.iterdir())

    for filename in filelist:

        filename=Path(filename).stem+".template"
    
        create_csv(filename,foldername)
elif(mode_value == 'oep'):
    folderpath = Path("Data/Templates/oepsoaptemplates")
    foldername='oepsoaptemplates'
    filelist=list(folderpath.iterdir())

    for filename in filelist:

        filename=Path(filename).stem+".template"
    
        create_csv(filename,foldername)
elif(mode_value == 'flist'):
    
    folderpath = Path("Data/Templates/opcodetemplates")
    filelist=list(folderpath.iterdir())
    foldername='opcodetemplates'
    for filename in filelist:

        filename=Path(filename).stem+".template"
        #print(filename)
        multiapilist=["changeplan.yaml.template","addplan.yaml.template"]
        if(filename not in multiapilist):
            var=flist_validation("Data/Templates/opcodetemplates/"+filename)
            if(var != 'VALID'):
                print(filename,var)
        create_csv(filename, foldername)
    print ("csv files are generated with templates")
elif(mode_value == 'rest'):
## Calling ##
    for root, dirs, files in os.walk("Data/Templates/resttemplates"):
        for file in files:
            if file.startswith("rest") and file.endswith(".template"):
                jsonToCSV(os.path.join(root, file),os.path.join("Data/csvfiles/restapi", file.removeprefix("rest").removesuffix(".template")+".csv"))
elif(mode_value == 'gui'):
    folderpath = Path("Data/Templates/guitemplates")
    foldername='guitemplates'
    filelist=list(folderpath.iterdir())

    for filename in filelist:

        filename=Path(filename).stem+".template"
    
        create_csv(filename,foldername)
else:
    print ("Please provide proper parameter value \n")
    print ("Valid values for csvgen are rest/soap/flist")
"""
