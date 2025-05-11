#!/usr/bin/env python -i
from robot.api import ResultWriter
from robot.running import TestSuite
#from robot.api import ResultWriter
from robot.libraries.BuiltIn import BuiltIn
import yaml
import merge
from yaml.loader import SafeLoader
import re
import sys


#Generic Api Call
def pvt_change():
    print("Enter the time which you want to modify in the Localconfig file")
    suite=TestSuite(name="Billing pvt",doc="Billing pvt change")
#print(pvt_time)
    suite.resource.imports.resource('../Resource/resources.robot')
    suite.setup.name='Open Connection And Log In'
    suite.teardown.name='Close All Connections'
    test=suite.tests.create("pvt")
#print(pvt_time)
    test.body.create_keyword("Set pvt date for billing")
    result=suite.run(output='Output/result/general.xml')  
    print("PVT Function Completed")
    ResultWriter('Output/Metrics/Result/output.xml').write_results(report='Output/Metrics/Result/report.html', log='Output/Metrics/Result/log.html')
    return;
##########run############
pvt_change();