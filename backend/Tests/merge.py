#!/usr/bin/env python
import sys
import os
from robot import rebot_cli
import subprocess

def collect_xmls(path, xmls):
    for filename in os.listdir(path):
        file_path = os.path.join(path,filename)
    
        if filename.endswith('.xml'):
            fullname = os.path.join(path, filename)
            xmls.append(file_path)
        
        if os.path.isdir(filename):
            collect_xmls(file_path, xmls)

def merge_output(op_dir):
    
    rebot_args = ['--name','Api','--output', 'Output\\Metrics\\Result\\output.xml','--log', 'Output\\Metrics\\Result\\log.html','--report','Output\\Metrics\\Result\\report.html']
    print(rebot_args)
    collect_xmls(op_dir, rebot_args)
    rebot_cli(rebot_args,exit=False)
    print("rebot_cli")
    