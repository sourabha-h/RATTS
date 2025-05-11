from string import Template
import json
import os


def generate_opcode(templatename,key,opcodename):

    opcode_name=templatename[0:templatename.find('.')]
    
    #open the template file
    with open('Data/Templates/opcodetemplates/'+templatename,'r') as f:
        src = Template(f.read())

    #read the json data
    jsonfile=open('Data/Input/jsonfiles/opcode/'+opcode_name+'.json','r')
    jsondata=jsonfile.read()
    obj=json.loads(jsondata)
    print(len(obj))
    print(obj)
    if(len(obj)==1):
        #load the jsondata
        
        result=src.substitute(**obj[key])
        with open('Data/Input/generatedopcode/'+opcodename+'_'+key+'.txt','w') as f:
            f.write(result)
        
    else:
        for i in range(len(obj)):
            #load the jsondata
            j=str(i+1)
            result=src.substitute(**obj[j])
            with open('Data/Input/generatedopcode/'+opcodename+'_'+j+'.txt','w') as f:
                f.write(result)
