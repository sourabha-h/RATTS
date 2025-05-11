from string import Template
from csvtojson import csvConvert
import json


def generate_request(templatename, key, arg1):

    opcode_name=templatename[0:templatename.find('.')]
    print(arg1)
    #open the template file
    if(arg1=='oep'):
        with open('Data/Templates/oepsoaptemplates/'+templatename,'r') as f:
            src = Template(f.read())
    else:
        with open('Data/Templates/soaptemplates/'+templatename,'r') as f:
            src = Template(f.read())

    #read the json data
    if(arg1=='oep'):
        jsonfile=open('Data/Input/jsonfiles/oepsoap/'+opcode_name+'.json','r')
    else:
        jsonfile=open('Data/Input/jsonfiles/soap/'+opcode_name+'.json','r')
    jsondata=jsonfile.read()
    
    #load the jsondata
    obj=json.loads(jsondata)
    
    result=src.substitute(obj[key])
    if(arg1=='oep'):
        with open('Data/Input/oepsoapRequestXmls/oepsoaprequest.xml','w') as f:
            f.write(result)
    else:
        with open('Data/Input/soapRequestXmls/soaprequest.xml','w') as f:
            f.write(result)