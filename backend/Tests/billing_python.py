#!/usr/bin/env python -i
from robot.running import TestSuite
#from robot.api import ResultWriter
from robot.libraries.BuiltIn import BuiltIn
import json
#from csvtojson import csvConvert
#from csvtojson import inserttocsv
import yaml
import merge
from yaml.loader import SafeLoader
import re
import csv
import getdata
import sys
from robot import rebot

objdata=None

#Generic Api Call

print("Enter the time which you want to modify in the Localconfig file")
suite=TestSuite(name="Billing pvt",doc="Billing pvt change")
#print(pvt_time)
suite.resource.imports.resource('../Resource/resources.robot')
suite.setup.name='Open Connection And Log In'
suite.teardown.name='Close All Connections'
test=suite.tests.create("pvt")
#print(pvt_time)
test.body.create_keyword("Set pvt date for billing")
result=suite.run(output='../Output/result/general.xml')  
print("PVT Function Completed")