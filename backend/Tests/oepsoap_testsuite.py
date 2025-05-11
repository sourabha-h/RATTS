from Tests.csvtojson import csvConvert
import json
import sys
from robot.running import TestSuite
from robot.api import ResultWriter
from robot.libraries.BuiltIn import BuiltIn
import subprocess
from Tests.responsetestcase import responseData
from Tests.cleanup import clearLogFiles
import os
def process_oepsoap(test_name,modex=""):
        clearLogFiles()
        jsonfile=open('Data/config/oepsoap_requests.json','r')
        jsondata=jsonfile.read()
    
        #load the jsondata
        obj=json.loads(jsondata)
        opcodes=obj['oep_operation']
        # Get the path four levels up from the current file
        path_four_levels_up = os.path.join(os.path.dirname(__file__), '..', '..', '..')
    
        # Convert to an absolute path
        absolute_path = os.path.abspath(path_four_levels_up)
        library_path = os.path.join(absolute_path,'RATTS', 'backend', 'Tests', 'soaprequestgeneration.py')
        resource_path = os.path.join(absolute_path,'RATTS', 'backend', 'Resource', 'oepsoapresources.robot')
        #D:\\OneDrive - BlueRose Technologies Pvt. Ltd\\Robot\\RATTS\\backend\\Resource\\resources.robot
        print(f"The absolute_path is: {absolute_path}")
        print(f"The resource_path is: {library_path}")
        print(f"The resource_path is: {resource_path}")
        
        # Replace backslashes with double backslashes
        modified_library_path = library_path.replace('\\', '\\\\')
        modified_resource_path = resource_path.replace('\\', '\\\\')
        # Print the modified path
        print(f"The new library path is: {modified_library_path}")
        print(f"The new resource path is: {modified_resource_path}")


        #create dynamic test suit
        suite=TestSuite(name="Soap Test Validation",doc="Calling API and validating the response")
        suite.resource.imports.library(modified_library_path)
        suite.resource.imports.resource(modified_resource_path)

        if(test_name == "All"):
            for opcodetest in opcodes:
                opcode=opcodes[opcodetest]
                csv_path=opcode.replace('-','').lower()+"_template.csv"
                template_name=opcode.replace('-','').lower()+".yaml.template"
                json_name=opcode.replace('-','').lower()+".json"
                csvConvert(csv_path,"oepsoap")
                jsondatafile=open('Data/Input/jsonfiles/oepsoap/'+json_name,'r')
                jsond=jsondatafile.read()

                #load the jsondata
                obj=json.loads(jsond)
                for  key  in  obj:
                    test=suite.tests.create(opcode+" Valid Case"+key,doc=opcode+ " with Valid Data"+key)
                    #test.body.create_keyword("Generate request",args=[template_name,key])
                    test.body.create_keyword("Check soap call",args=[json_name,template_name,opcode,key])
        else:
            opcode=opcodes[test_name]
            print(opcode)
            csv_path=opcode.replace('-','').lower()+"_template.csv"
            template_name=opcode.replace('-','').lower()+".yaml.template"
            json_name=opcode.replace('-','').lower()+".json"
            print(json_name)
            csvConvert(csv_path,"oepsoap")
            jsondatafile=open('Data/Input/jsonfiles/oepsoap/'+json_name,'r')
            jsond=jsondatafile.read()
            print(jsond)
            #load the jsondata
            obj=json.loads(jsond)
            for  key  in  obj:
                test=suite.tests.create(opcode+" Valid Case"+key,doc=opcode+ " with Valid Data"+key)
                #test.body.create_keyword("Generate request",args=[template_name,key])
                test.body.create_keyword("Check soap call",args=[json_name,template_name,opcode,key])

        result=suite.run(output='Output/Metrics/Result/output.xml')
        ResultWriter('Output/Metrics/Result/output.xml').write_results(report='Output/Metrics/Result/report.html', log='Output/Metrics/Result/log.html')
         #generating metrics report
        command = r"py .\\Output\\Metrics\\runner.py -I .\\Output\\Metrics\\Result --logo ../Images/BRT_LOGO.png"
        # Execute the command and capture the output and errors
        subprocess.run(command, shell=True, capture_output=True, text=True)
        res= responseData()
        print(res)
        return res