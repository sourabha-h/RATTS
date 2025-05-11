from robot.running import TestSuite
#from robot.api import ResultWriter
from robot.libraries.BuiltIn import BuiltIn
import json
from Tests.csvtojson import csvConvert
from Tests.csvtojson import inserttocsv
import yaml
from Tests.merge import *
from yaml.loader import SafeLoader
import re
import csv
from Tests.getdata import *
from robot import rebot
from Tests.db_query import db_query
import sys
import os
from Tests.responsetestcase import responseData
from Tests.cleanup import clearLogFiles
import subprocess
objdata=None

#Generic Api Call
def genericApiCall(opcodes,opcodekey,suite):
    print("genericApiCall is called")
    if opcodekey == "All":
        for opcodetest in opcodes:
            opcode=opcodes[opcodetest]
            csv_path=opcode.replace('_','').lower()+"_template.csv"
            print(csv_path)
            template_name=opcode.replace('_','').lower()+".yaml.template"
            opcodename=opcode.replace('_','').lower()
            csvConvert(csv_path,"opcode")
            jsondt="Data/Input/jsonfiles/opcode/"+opcode.replace('_','').lower()+".json"
            #read the json data
            jsonf=open(jsondt,'r')
            jsond=jsonf.read()

            #load the jsondata
            obj1=json.loads(jsond)
            for key in obj1:
                test=suite.tests.create(opcode+" Valid Case "+key,doc=opcode+ " with Valid Data "+key)
                test.body.create_keyword("Generate Opcode in Loop",args=[template_name,key,opcodename])
    else:
        print("Entered for individual testing")
        opcode=opcodes[opcodekey]
        print("opcode  :  "+opcode)
        csv_path=opcode.replace('_','').lower()+"_template.csv"
        print(csv_path);
        template_name=opcode.replace('_','').lower()+".yaml.template"
        opcodename=opcode.replace('_','').lower()
        csvConvert(csv_path,"opcode")
        jsondt="Data/Input/jsonfiles/opcode/"+opcode.replace('_','').lower()+".json"
        #read the json data
        jsonf=open(jsondt,'r')
        jsond=jsonf.read()

        #load the jsondata
        obj1=json.loads(jsond)
        for key in obj1:
            test=suite.tests.create(opcode+" Valid Case "+key,doc=opcode+ " with Valid Data "+key)
            test.body.create_keyword("Generate Opcode in Loop",args=[template_name,key,opcodename])
           
#Multi Task Api Call
def multiTaskApiCall(itervalue,test,scenario_csv_path,tsk):
    key="1"
    res=[]
    print("This is the value passed in tsk parameter", tsk)
    
    i=0
    textfile=[]
    objdata=getcsvdata(scenario_csv_path,tsk)
    print ("This is objdata", objdata)
    for item in itervalue:
        print("This is the print statement for item from itervalue", item)
        seq=item.get('sequence')
        opcode1=item.get('opcode')
        pickdata=item.get('loop')
        csv_path=opcode1.replace('_','').lower()+"_template.csv"
        template_name=opcode1.replace('_','').lower()+".yaml.template"
        opcodena=opcode1.replace('_','').lower()+"_"+key+".txt"
        textfile.append(opcodena)
        opcodename=opcode1.replace('_','').lower()
        params=[]
        if(seq==1):
            inserttocsv(csv_path,objdata)
            csvConvert(csv_path,"opcode")
            test.body.create_keyword("Generate Opcode",args=[template_name,key,opcodename])
            test.body.create_keyword("Get Data From Opcode",args=[opcodena])
    
                        
        if(i!=0):
                j=0
                params.append(getParameters(template_name))                                          
                test.body.create_keyword('Get Data From File',args=[textfile,params[j],csv_path,objdata])        
                test.body.create_keyword("Csv Convert",args=[csv_path,"opcode"])
                test.body.create_keyword("Generate Opcode",args=[template_name,key,opcodename])
                if(pickdata==1):
                    opcode_name=template_name[0:template_name.find('.')]
                    #read the json data
                    jsonfile=open('Data/Input/jsonfiles/'+opcode_name+'.json','r')
                    jsondata=jsonfile.read()
                    obj=json.loads(jsondata)
                    test.body.create_keyword("Get Data From Opcode In Loop",args=[opcodename,obj]) 
                else:
                      test.body.create_keyword("Get Data From Opcode",args=[opcodena])
                j=j+1
        i=i+1
        
        


#get CSV Data
def getcsvdata(scenario_csv_path,tsk):
        csvConvert(scenario_csv_path,"opcode")
        jsondt="Data/Input/jsonfiles/opcode/"+tsk.replace('_','').lower()+".json"
        #read the json data
        jsonf=open(jsondt,'r')
        jsond=jsonf.read()
        print("This is the value of .json files from csvconvert", jsond)

        #load the jsondata
        objdata=json.loads(jsond)
        return objdata
       
        


#getting Parameters
def getParameters(templatename):
    # Open the file and load the file
    with open('Data/Templates/opcodetemplates/'+templatename,'r') as f:
        data = yaml.load(f, Loader=SafeLoader)
    pat = r'(?<=\{).+?(?=\})'
    dataarr=re.findall(pat,data)
    return dataarr


def process_opcode(opcodekey,modex=""):
        clearLogFiles()
        print("Backend:"+opcodekey)
        print("modex:"+modex)
        #read the json data
        jsonfile=open('Data/config/opcodes.json','r')
        jsondata=jsonfile.read()
        print ("This is reading the json data from opcodes.json file ", jsondata)
        #load the jsondata 
        obj=json.loads(jsondata)
        opcodes=obj['opcodes']
        print ("This is the loading of jsondata objects obj", opcodes)
        # Get the path four levels up from the current file
        path_four_levels_up = os.path.join(os.path.dirname(__file__), '..', '..', '..')
    
        # Convert to an absolute path
        absolute_path = os.path.abspath(path_four_levels_up)
        library_path = os.path.join(absolute_path,'RATTS', 'backend', 'Tests', 'opcodegeneration.py')
        resource_path = os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'resources.robot')
        #D:\\OneDrive - BlueRose Technologies Pvt. Ltd\\Robot\\RATTS\\backend\\Resource\\resources.robot
        print(f"The absolute_path is: {absolute_path}")
        print(f"The library_path is: {library_path}")
        print(f"The resource_path is: {resource_path}")
        
        # Replace backslashes with double backslashes
        modified_library_path = library_path.replace('\\', '\\\\')
        modified_resource_path = resource_path.replace('\\', '\\\\')
        # Print the modified path
        print(f"The new library path is: {modified_library_path}")
        print(f"The new resource path is: {modified_resource_path}")

        #generating test cases
        for x in opcodes:
            print("modex in the loop"+modex)
            print("x in the loop"+x)
           
            if(x=="general"):
                
                if(modex.strip()=="general" or modex.strip()==""):
                    print("xxxxxxxxxxxxxxxx")
                    #create dynamic test suit
                    suite=TestSuite(name="General Opcode Test Cases",doc="Requesting General opcode and validating the response")
                    #suite.resource.imports.library(r'C:\\xampp\\htdocs\\RATTS\\backend\\Tests\\opcodegeneration.py')
                    #suite.resource.imports.resource(r'C:\\xampp\\htdocs\\RATTS\\backend\\Resource\\resources.robot')
                    suite.resource.imports.library(modified_library_path)
                    suite.resource.imports.resource(modified_resource_path)
                    suite.setup.name='Open Connection And Log In'
                    suite.teardown.name='Close All Connections'
                   
                    print("opcodekey  :: "+opcodekey)
                    genericApiCall(opcodes[x],opcodekey,suite) 
                    # Execute suite. Notice that log and report needs to be created separately.
                    #f = open('Output/result/general.xml', 'r+')
                    #f.truncate(0)
                    #f.close()
                    result=suite.run(output='Output/Metrics/Result/general.xml')       
            
            if(x=="multitask" and (modex== x or modex == "")):
                if(opcodekey=='All'):
                    for y in opcodes[x]:
                            print ("This is y value",y)
                            tsk=y
                            #create dynamic test suit
                            suite=TestSuite(name=tsk+" Opcode Test Cases",doc="Requesting Multitask opcode and validating the response")
                            #suite.resource.imports.library(r'C:\\xampp\\htdocs\\RATTS\\backend\\Tests\\opcodegeneration.py')
                            #suite.resource.imports.resource(r'C:\\xampp\\htdocs\\RATTS\\backend\\Resource\\resources.robot')
                            suite.resource.imports.library(modified_library_path)
                            suite.resource.imports.resource(modified_resource_path)
                            suite.setup.name='Open Connection And Log In'
                            suite.teardown.name='Close All Connections'
                            task_scenario=tsk.replace('_','').lower()
                            print(task_scenario)
                            scenario_csv_path=tsk.replace('_','').lower()+"_template.csv"
                            print(scenario_csv_path)
                            test=suite.tests.create(tsk+" Valid Case",doc=tsk+ " with Valid Data")
                            itervalue = iter(opcodes['multitask'][tsk])
                            print ("This is value of itervalue", itervalue)
                            multiTaskApiCall(itervalue,test,scenario_csv_path,task_scenario)
                            # Execute suite. Notice that log and report needs to be created separately.
                            result=suite.run(output='Output/Metrics/Result/'+tsk+'.xml')
                else:
                    tsk=opcodekey
                    print ("This is tsk value",tsk)
                    
                    #create dynamic test suit
                    suite=TestSuite(name=tsk+" Opcode Test Cases",doc="Requesting Multitask opcode and validating the response")
                    #suite.resource.imports.library(r'C:\\xampp\\htdocs\\RATTS\\backend\\Tests\\opcodegeneration.py')
                    #suite.resource.imports.resource(r'C:\\xampp\\htdocs\\RATTS\\backend\\Resource\\resources.robot')
                   
                    suite.resource.imports.library(modified_library_path)
                    suite.resource.imports.resource(modified_resource_path)
                    suite.setup.name='Open Connection And Log In'
                    suite.teardown.name='Close All Connections'
                    task_scenario=tsk.replace('_','').lower()
                    print(task_scenario)
                    scenario_csv_path=tsk.replace('_','').lower()+"_template.csv"
                    print(scenario_csv_path)
                    test=suite.tests.create(tsk+" Valid Case",doc=tsk+ " with Valid Data")
                    itervalue = iter(opcodes['multitask'][tsk])
                    print ("This is value of itervalue", itervalue)
                    multiTaskApiCall(itervalue,test,scenario_csv_path,task_scenario)
                    # Execute suite. Notice that log and report needs to be created separately.
                    result=suite.run(output='Output/Metrics/Result/'+tsk+'.xml')
                         
        merge_output('Output/Metrics/Result')
        #generating metrics report
        command = r"py .\\Output\\Metrics\\runner.py -I .\\Output\\Metrics\\Result --logo ../Images/BRT_LOGO.png"
        # Execute the command and capture the output and errors
        subprocess.run(command, shell=True, capture_output=True, text=True)
        res= responseData()
        print(res)
        return res