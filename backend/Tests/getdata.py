import sys
import re
import struct
import tempfile
import os
import re
from sys import argv


def format_data(filename):
    Dict = {}
    array_name = ""
    line_no_lvl0 = 0
    line_no_lvl1 = 0
    flag = 0
    delete_list = ["STR [0]", "ENUM [0]", "DECIMAL [0]","POID [0]","TSTAMP [0]","INT [0]"]
    array_list = ["ARRAY","SUBSTRUCT"]
    flag = 0
    fin = open(filename)
    fout = open(filename + '.tmp', 'w')
    #lines = fin.readlines()
    for i, line in enumerate(fin):
        if i > 1:    
    #for line in lines:
            for word in delete_list:
                line = line.replace(word, "##")
                #line = line.strip()
            
            if ('ARRAY' in line or 'SUBSTRUCT' in line) and (line[0] == "0"):
                line_no_lvl0 = i+1;
                array_lvl_0 = line.split()[1]
                
            if ('ARRAY' in line ) and (line[0] == "1"):
                    array_lvl_1 = line.split()[1]
                    line_no_lvl1 = i+1;
                
            if ('ARRAY' not in line) and (line[0] == "1"):
                field_lvl_1 = line.split()[1]
           
                modified_field_lvl_1 = array_lvl_0+"_"+field_lvl_1
                line = line.replace(field_lvl_1, modified_field_lvl_1)
            
            if ('ARRAY' not in line) and (line[0] == "2"):
                field_lvl_2 = line.split()[1]
           
                modified_field_lvl_2 = array_lvl_0+"_"+array_lvl_1+"_"+field_lvl_2
                line = line.replace(field_lvl_2, modified_field_lvl_2)
            
            if (line.find('ARRAY') == -1) :
                if (line.find('SUBSTRUCT') == -1) :
                #line  = re.sub(r"[\t]*", "", line)
                    line = line.lstrip()
                    fout.write(line[2:]) 
    fout.close()
    fin.close()
    outname = fout.name
    os.remove(filename)  
    os.rename(outname, filename)

  
def get_data(filename,fieldname):
    #format_data(filename)
    fieldvalue = {}
    mydict = {}
   
    with open(filename, "r") as infile: 
        for line in infile: 
            key, value = line.strip().split('##') 
            key = re.sub(r"[\t\s]*", "", key)
            value = value.strip()
            value = value.strip('"')
            if key in mydict:
                if isinstance(mydict[key],list):
                    mydict[key].append(value)
                else:
                    val= mydict[key]                
                    mydict[key]=[]
                    mydict[key].append(val)
                    mydict[key].append(value)
            else:
                mydict[key] = (value) 
    #print(mydict)
    for x in fieldname:
       
            value= mydict[x]
            fieldvalue[x]=(value)

    print(fieldvalue) 
    
    return fieldvalue
