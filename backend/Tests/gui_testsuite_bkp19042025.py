from robot.running import TestSuite
from robot.running.model import Keyword
from robot.api import ResultWriter
from robot.libraries.BuiltIn import BuiltIn
import json
from Tests.csvtojson import csvConvert
import yaml
from Tests.merge import merge_output
from yaml.loader import SafeLoader
import re
import csv
#from Tests.getdata import getdata
from robot import rebot
import subprocess
from Tests.responsetestcase import responseData
from Tests.cleanup import clearLogFiles
import os
import copy
import shutil

#get CSV Data
def getcsvdata(scenario_csv_path,tsk):
        print(tsk)
        csvConvert(scenario_csv_path,"gui")
        jsondt="Data/Input/jsonfiles/gui/"+tsk.replace('_','').lower()+".json"
        #read the json data
        jsonf=open(jsondt,'r')
        jsond=jsonf.read()
        print("This is the value of .json files from csvconvert", jsond)

        #load the jsondata
        objdata=json.loads(jsond)
        return objdata

def process_gui(test_name,modex=""):
        clearLogFiles()
        #read the json data
        jsonfile=open('Data/config/gui_url.json','r')
        jsondata=jsonfile.read()
        #load the jsondata 
        obj=json.loads(jsondata)
        urls=obj['urls']
        # Get the path four levels up from the current file
        path_four_levels_up = os.path.join(os.path.dirname(__file__), '..', '..', '..')

        # Convert to an absolute path
        absolute_path = os.path.abspath(path_four_levels_up)
        resource_path = os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'gui_resources.robot')
        test_suite_path=""
        
        print(f"The absolute_path is: {absolute_path}")
        print(f"The resource_path is: {resource_path}")

        modified_resource_path = resource_path.replace('\\', '\\\\')
        modified_test_suite_path=""
        print(f"The new resource path is: {modified_resource_path}")

        suite=TestSuite(name="GUI Test Cases",doc="Auto Fill Form and click action and validating the response")
        suite.resource.imports.resource(modified_resource_path)
        total_key=1
        if(test_name=="All"):
                grobot_folder = os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'generated_suite')
                modified_grobot_path=grobot_folder.replace('\\', '\\\\')
                shutil.rmtree(modified_grobot_path)
                suite_keywords=[]
                x="login"
                url=urls[x]
                print(url)
                tsk = x
                
                scenario_csv_path=x.replace('_','').lower()+"_template.csv"
                template_file=x.replace('_','').lower()+".yaml.template"
                print(template_file)
                objdata=getcsvdata(scenario_csv_path,tsk)
                print(objdata)                                
                for key in  objdata:
                        print(f"inner loop data: {objdata[key]}")                            
                        first_key = next(iter(objdata[key]))
                        tetestcase_key = objdata[key]["testcase"]
                        del objdata[key][first_key]
                        name=f"{x+" "+tetestcase_key}"
                        doc=f"{x+" with Keyword  "+tetestcase_key}"
                        del objdata[key]["testcase"]
                        json_objdata=json.dumps(objdata[key])
                        steps_name="Page Action"
                        steps_args=[json_objdata,template_file,url]
                        suite_keywords.append({"name":name,"doc":doc,"steps":[{"name":steps_name,"args":steps_args}]})
                
                total_key=key 
                print(suite_keywords)
                i=1
                for keyword in suite_keywords:
                        for x in urls:
                            if(x!="login"):
                                url=urls[x]
                                print(url)
                                tsk = x
                                
                                scenario_csv_path=x.replace('_','').lower()+"_template.csv"
                                template_file=x.replace('_','').lower()+".yaml.template"
                                print(template_file)
                                objdata=getcsvdata(scenario_csv_path,tsk)
                                print(objdata)
                                
                                                
                                obj=copy.deepcopy(objdata)
                                for key in  obj:
                                        print(f"inner loop data: {obj[key]}")                            
                                        first_key = next(iter(obj[key]))
                                        first_key_val=int(obj[key][first_key])
                                        testcase_key = obj[key]["testcase"]
                                        del obj[key][first_key]
                                        test=suite.tests.create(x+" Test Case for "+testcase_key,doc=x+" with Test  "+testcase_key)
                                        del obj[key]["testcase"]
                                        json_objdata=json.dumps(obj[key])
                                        
                                        print(f"first_key_val: {first_key_val}")
                                        test.body.create_keyword("Page Action",args=[json_objdata,template_file,url])
                        
                        #writing into a file
                        foldername=f"user{i}"
                        user_folder = os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'generated_suite', foldername)

                        # Create the user folder if it doesn't exist
                        os.makedirs(user_folder, exist_ok=True)

                        # Define the file path
                        test_suite_path = os.path.join(user_folder, "test_suite.robot")
                        modified_test_suite_path=test_suite_path.replace('\\', '\\\\')
                        generate_robot(modified_resource_path,modified_test_suite_path,suite,test_name,keyword)
                        i=i+1
                        suite.tests.clear()
        elif(test_name =="login"):
                                grobot_folder = os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'generated_suite')
                                modified_grobot_path=grobot_folder.replace('\\', '\\\\')
                                shutil.rmtree(modified_grobot_path)
                                url= urls[test_name]
                                print(url)
                                tsk = test_name                          
                                scenario_csv_path=test_name.replace('_','').lower()+"_template.csv"
                                template_file=test_name.replace('_','').lower()+".yaml.template"
                                print(template_file)
                                objdata=getcsvdata(scenario_csv_path,tsk)
                                print(objdata)
                                i=1
                                for key in  objdata:
                                        
                                        print(f"inner loop data: {objdata[key]}")                            
                                        first_key = next(iter(objdata[key]))
                                        testcase_key = objdata[key]["testcase"]
                                        print(testcase_key)
                                        del objdata[key][first_key]
                                        test=suite.tests.create(test_name+" Test Case "+testcase_key,doc=test_name+" For Test  "+testcase_key)
                                        del objdata[key]["testcase"]
                                        test.setup.name="Open Application"
                                        test.teardown.name="Close Application"
                                        json_objdata=json.dumps(objdata[key])
                                        test.body.create_keyword("Page Action",args=[json_objdata,template_file,url])
                                        foldername=f"user{i}"
                                        user_folder = os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'generated_suite', foldername)

                                        # Create the user folder if it doesn't exist
                                        os.makedirs(user_folder, exist_ok=True)

                                        # Define the file path
                                        test_suite_path = os.path.join(user_folder, "test_suite.robot")
                                        modified_test_suite_path=test_suite_path.replace('\\', '\\\\')
                                        generate_robot(modified_resource_path,modified_test_suite_path,suite,test_name,keyword="")
                                        i=i+1
                                        suite.tests.clear()
                                total_key=key       
        else:
             
                grobot_folder = os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'generated_suite')
                modified_grobot_path=grobot_folder.replace('\\', '\\\\')
                shutil.rmtree(modified_grobot_path)
                suite_keywords=[]
                                                                
                x="login"
                url= urls[x]
                print(url)
                tsk = x                              
                scenario_csv_path=x.replace('_','').lower()+"_template.csv"
                template_file=x.replace('_','').lower()+".yaml.template"
                print(template_file)
                objdata=getcsvdata(scenario_csv_path,tsk)
                print(objdata)
                for key in  objdata:
                        print(f"inner loop data: {objdata[key]}")                            
                        first_key = next(iter(objdata[key]))
                        tetestcase_key = objdata[key]["testcase"]
                        del objdata[key][first_key]
                        name=f"{x+" "+tetestcase_key}"
                        doc=f"{x+" with Keyword  "+tetestcase_key}"
                        del objdata[key]["testcase"]
                        json_objdata=json.dumps(objdata[key])
                        steps_name="Page Action"
                        steps_args=[json_objdata,template_file,url]
                        suite_keywords.append({"name":name,"doc":doc,"steps":[{"name":steps_name,"args":steps_args}]})

                total_key=key 
                x=test_name
                url= urls[x]
                print(url)
                tsk = x                              
                scenario_csv_path=x.replace('_','').lower()+"_template.csv"
                template_file=x.replace('_','').lower()+".yaml.template"
                print(template_file)
                objdata=getcsvdata(scenario_csv_path,tsk)
                print(objdata)
                print(suite_keywords)
                i=0
                for keyword in suite_keywords:
                        i=i+1
                        suite.tests.clear()
                        for step in keyword['steps']:
                                print(step)
                                obj=copy.deepcopy(objdata)
                        
                                for key in  obj:
                                        print(f"inner loop data: {obj[key]}")                            
                                        first_key = next(iter(obj[key]))
                                        first_key_val=int(obj[key][first_key])
                                        testcase_key = obj[key]["testcase"]
                                        del obj[key][first_key]
                                        test=suite.tests.create(x+" Test Case for "+testcase_key,doc=x+" with Test  "+testcase_key)
                                        del obj[key]["testcase"]
                                        json_objdata=json.dumps(obj[key])

                                        print(f"first_key_val: {first_key_val}")
                                        test.body.create_keyword("Page Action",args=[json_objdata,template_file,url])

                        #writing into a file
                        foldername=f"user{i}"
                        user_folder = os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'generated_suite', foldername)

                        # Create the user folder if it doesn't exist
                        os.makedirs(user_folder, exist_ok=True)

                        # Define the file path
                        test_suite_path = os.path.join(user_folder, "test_suite.robot")
                        #test_suite_path=os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'generated_suite',foldername,'test_suite.robot')
                        modified_test_suite_path=test_suite_path.replace('\\', '\\\\')
                        generate_robot(modified_resource_path,modified_test_suite_path,suite,test_name,keyword)
        generated_suite_path=os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'generated_suite\\')
        modified_generated_suite_path=generated_suite_path.replace('\\', '\\\\')
        print("entered into the pabot")
        command = f"pabot --processes {total_key}  --outputdir Output/result --output output.xml --log log.html --report report.html  {modified_generated_suite_path}"
        print(command)
        result=subprocess.run(command, shell=True, capture_output=True, text=True)
       
        #result=suite.run(output='Output/result/gui.xml')
        print(f"Return Code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")      
        merge_output('Output/result')
        #generating metrics report
        command = r"py .\\Output\\Metrics\\runner.py -I .\\Output\\result --logo ../Images/BRT_LOGO.png"
        # Execute the command and capture the output and errors
        result1=subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Return Code: {result1.returncode}")
        print(f"STDOUT: {result1.stdout}")
        print(f"STDERR: {result1.stderr}")
        
        res= responseData()
        print(res)
        return res

def generate_robot(modified_resource_path,modified_test_suite_path,suite,test_name,keyword):
        with open(modified_test_suite_path, "w") as file:
                file.write("*** Settings ***\n")
                file.write("Documentation    Gui Resources\n")
                file.write(f"Resource         {modified_resource_path}\n")
                if(test_name !="login"):
                        suite.setup.name=keyword["name"]
                        suite.teardown.name="Close Application"
                if(suite.setup.name):
                        file.write(f"Suite Setup    {suite.setup.name}\n")
                if(suite.teardown.name):
                        file.write(f"Suite Teardown    {suite.teardown.name}\n")
                file.write("\n")
                if(keyword !=""):
                        file.write("*** Keywords ***\n")
                        
                        file.write(f"{keyword['name']}\n")
                        file.write(f"    [Documentation]    {keyword['doc']}\n")
                        file.write(f"    Open Application\n")
                        for step in keyword['steps']:
                                args = "    ".join(step["args"])
                                file.write(f"    {step['name']}    {args}\n")
                        file.write("\n")

                file.write("\n")
                
                file.write("*** Test Cases ***\n")
                for test in suite.tests:
                        file.write(f"{test.name}\n")
                        file.write(f"    [Documentation]    {test.doc}\n")
                        print(f"test.setup {test.setup}")
                        if(test.setup.name):
                                file.write(f"    [Setup]    {test.setup.name}\n")
                        if(test.teardown.name):
                                file.write(f"    [Teardown]    {test.teardown.name}\n")
                        
                        for keyword in test.body:
                                keyword_args='    '.join(map(str, keyword.args))
                                #keyword_args='    {"username": "rajeswari@bluerose-tech.com", "password-input": "U238Vr%*7i3Lgab", "page-title-box": "Overview"}    login.yaml.template    login.html'
                                file.write(f"    {keyword.name}    {keyword_args}\n")
                        file.write("\n")
        