import pandas as pd
import re
import numpy as np
from Tests.db_query import db_query
import sys
import struct
import tempfile
import os
from sys import argv
import sys

def format_val_data(filename):
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
                line_no_lvl0 = i+1
                array_lvl_0 = line.split()[1]
                
            if ('ARRAY' in line ) and (line[0] == "1"):
                    array_lvl_1 = line.split()[1]
                    line_no_lvl1 = i+1
                
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

  
def get_val_data(filename,fieldname):
    #format_val_data(filename)
    value = 0
    fieldvalue = {}
    mydict = {} 
    with open(filename, "r") as infile: 
        for line in infile: 
            #print(line)
            key,value = line.strip().split('##') 
            key = re.sub(r"[\t\s]*", "", key)
            value = value.strip()
            value = value.strip('"')
            mydict[key] = (value) 
    #print(mydict)
    #print(fieldname)
    
    value= mydict[fieldname]
        #fieldvalue[x]=(value)

    #print(value) 
    
    return value
def runner_validate(opcodename,key):
    cnt=0
    status=''
    test_case_no=''
    test_case_name=''
    test_status=''
    query_cnt=0
    field_value=''             
    validate_name=opcodename.replace('_','').lower()+".validate"
    output_name=opcodename.replace('_','').lower()+"_"+key+".txt"
    outputfile= "Data/output/"+output_name
    validatefile="Data/validate/"+validate_name
    
    if ((os.stat("Data/validate/"+validate_name).st_size == 0)== True):
        print("Validation File is empty")
        status=1
        return status
    else:
        validatefilename= open("Data/validate/"+validate_name,mode='r',encoding='utf8', newline='\r\n')
        outputfile= "Data/output/"+output_name
        #format_val_data(outputfile)
        #validatefilename= open(validatefile,'r')
   # df_ops = pd.read_csv('../Data/output/cus_ops_fields.dat', header=None)

    # Import the struct library


# use enumerate to show that second line is read as a whole
        for i, line in enumerate(validatefilename):   
            query_cnt=0
            for j in range(len(line.split(';'))):
                number = len(line.split(';'))
                value=line.split(';')[j]
                test_case_no=line.split(';')[0]
                test_case_name=line.split(';')[1]
                #print("seema",value)
                #testcaseno=line.split(';')[1]
                #query_cnt=0
                if (len(value.split(',')) > 1):
                    field_name=value.split(',')[0]
                    #print("seema11",field_name)
                    #print(outputfile)
    
                    
                    
                    table_name=value.split(',')[1]
                    #print("seema11",table_name)
                    field_value=get_val_data(outputfile,field_name)
                #print ("seema",field_value)
                    count = len(field_value.split())
                    if (count > 1):
                        field_value=field_value.split()[2]
                        #print("seema"+field_value)
                    else:
                        field_value=field_value
                   
                     
                    query_cnt=query_cnt+1;   
                    sql,st =db_query(table_name,field_value)
                    sql_query=sql
                    print("*********************************")
                    print("TEST CASE : "+test_case_no )
                    print("QUERY : "+str(query_cnt) + "--->" + sql_query)
                    print("TEST CASE QUERY STATUS :"+st)
                    print("*********************************")
                            #query_cnt=query_cnt+1; 
                            #status=st
                           
            if(st=='FAILURE'):
                cnt=cnt+1  
                break
        if (cnt>0):
            test_status='FAILURE'
        else:
            test_status='SUCCESS' 

        print("=========SUMMARY STARTS===================================")     
        print("TEST CASE DATA :"+"{"+line+"}")         
        print("TEST CASE NUMBER :"+test_case_no) 
        print("TEST CASE NAME :"+test_case_name) 
        print("OVERALL TEST CASE STATUS SUMMARY :"+test_status)
        print("==========SUMMARY ENDS=========================================")

    if (cnt>0):
        status=1
    else:
        status=0
        #    print("se1",j)
    return status
#final_status=runner_validate("CUS_OP_PYMT_POL_COLLECT","1")  
#print(final_status) 


