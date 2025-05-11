import csv
import json
import re
import pandas as pd


def csvConvert(csv_path,system):
    opcode_name=csv_path[0:csv_path.find('_')]
    jsonData = {}
    with open('Data/csvfiles/'+system+'/'+csv_path,'r',encoding="latin 1") as csvfile:
        csvData = csv.DictReader(csvfile)
        for rows in csvData:
            key = rows['no']
            jsonData[int(key)] = rows
    
    with open('Data/Input/jsonfiles/'+system+'/'+opcode_name+'.json','w',encoding="latin 1") as jsonfile:
        jsonfile.write(json.dumps(jsonData))


#insert data in csv file
def inserttocsv(csv_path,objdata):
    data = []
    key='1'
    sz=0
    fl=''
    
    if(objdata.get(key) is not None):
        for ky in objdata[key].keys():
            if(type(objdata[key][ky])== list):
                sz=len(objdata[key][ky])
                fl=ky
                break
    else:
        for ky in objdata.keys():
            if(type(objdata[ky]== list)):
                sz=len(objdata[ky])
                fl=ky
                break    
    with open("Data/csvfiles/opcode/"+csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        
        for row in reader:
            
            if(objdata.get(key) is not None):
                for k in row:
                    if (fl !=''):  
                        data = [(index+1, value) for index, value in enumerate(objdata[key][fl])] 
                        """for i in range(sz):
                            
                            data.append(i)
                            data.append(objdata[key][fl][i])"""
                        break
    
                    else:
                        if(re.search(r'\d',k)):
                            k=k[0:-1]
                            data.append(objdata[key][k])
                        else:
                            data.append(objdata[key][k])


            else:
                for k in row:
                    if (fl !=''):    
                            data = [(index+1, value) for index, value in enumerate(objdata[fl])] 
                            """for i in range(sz):
                                data[i]=[]
                                data[i].append(i)
                                data[i].append(objdata[k][i])"""
                               
                            break
                        
                    else:
                        if(re.search(r'\d',k)):
                            k=k[0:-1]
                            data.append(objdata[k])
                        else:
                            data.append(objdata[k])
            with open("Data/csvfiles/opcode/"+csv_path, 'w+') as f:  
                        obj1=csv.writer(f) 
                        obj1.writerow(row)
                        contains_sets = all(len(set(item)) == len(item) for item in data)
                        if(contains_sets):
                            for item in data:
                                 obj1.writerow(item)
                        else:    
                            obj1.writerow(data)         
                        #data.append(list(map(objdata.get, row)))
            break
        
            

def merge_dictionaries(dct1,dct2):
    x=dct1.copy()
    x.update(dct2)
    return x
        
## Function to convert csv to nested json ##
def csvToJSON(csv_file,json_file, sep="."):
    """
    The opposite of json_normalize
    """
    df = pd.read_csv(csv_file)
    result = []
    for idx, row in df.iterrows():
        parsed_row = {}
        for col_label,v in row.items():
            keys = col_label.split(sep)

            current = parsed_row
            for i, k in enumerate(keys):
                if i==len(keys)-1:
                    current[k] = v
                else:
                    if k not in current.keys():
                        current[k] = {}
                    current = current[k]
        # save
        result.append(parsed_row)
       
    json_string = json.dumps(result[0])
    with open(json_file, 'w') as f:
        f.write("%s\n" % json_string)
    return result[0]