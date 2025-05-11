import os
from pathlib import Path
import json
import re
import yaml
from collections import OrderedDict


def get_template_names(system_name):
    dir = f"Data/Templates/{system_name}"
    files = os.listdir(dir)
    files = [f for f in files if os.path.isfile(os.path.join(dir, f))]
    # Remove all extensions
    files = [f.split('.')[0] for f in files]
    file_names={}
    with open("displayname.json", "r") as file:
        display_name = json.load(file)
    
    for file in files:
        if file in display_name:
            file_names[file] = display_name[file]
    return file_names

# def get_system_name():
#     dir_path = "Data/Templates"
#     # List all entries in the directory
#     entries = os.listdir(dir_path)
#     # Filter to include only directories
#     directories = [entry for entry in entries if os.path.isdir(os.path.join(dir_path, entry))]
    
#     system_names = {}
    
#     # Load the JSON file
#     with open("displayname.json", "r") as file:
#         display_name = json.load(file)
    
#     for directory in directories:
#         if directory in display_name:
#             system_names[directory] = display_name[directory]

#     return system_names

def get_system_name():
    with open("system_name.json", 'r') as file:
        data = json.load(file)  # Load the JSON data
    return data

def parse_text_file(text_file_path):
    key_values = {}
    
    def extract_values(text):
        pattern = re.compile(r'(".*?")\s*:\s*(".*?")')
        matches = pattern.findall(text)
        return [{ 'value': match[0].strip('"'), 'description': match[1].strip('"') } for match in matches]

    def extract_nested_values(text):
        pattern = re.compile(r'(\[.*?\])\s*=\s*\{(.*?)\}', re.DOTALL)
        matches = pattern.findall(text)
        nested_dict = {}
        for match in matches:
            key = match[0].strip('["]')
            nested_dict[key] = extract_values(match[1])
        return nested_dict

    # Read the text file
    with open(text_file_path, 'r') as file:
        text = file.read()

    # Handle top level key-value pairs
    top_level_pattern = re.compile(r'(\w+)\s*=\s*\{(.*?)\}', re.DOTALL)
    matches = top_level_pattern.findall(text)
    for match in matches:
        key = match[0]
        value_text = match[1]
        key_values[key] = extract_values(value_text)
    
    # Handle nested key-value pairs
    nested_key_values = extract_nested_values(text)
    for key, value in nested_key_values.items():
        if key not in key_values:
            key_values[key] = value
        else:
            key_values[key].update(value)
    
    return key_values

def update_json_data_with_text_info(json_data, text_info):
    for item in json_data.values():
        for key in text_info:
            if key in item:
                item[key] = text_info[key]
    return json_data

def get_template_content(template_name, system_name):
    text_info = parse_text_file("addservice_mobile.txt")
    # text_info = parse_text_file("/home/sushmitha_m/fastapi/master_file.txt")
    dir_path = "Data/Templates"
    extension = "yaml.template"
    file_name = template_name + "." + extension
    folder_path = os.path.join(dir_path, system_name)
    file_path = os.path.join(folder_path, file_name)
    print(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'r') as yaml_file:
            yaml_content = yaml.safe_load(yaml_file)

        # Extract placeholders using regex while maintaining order
        placeholders = re.findall(r"\$\{(\w+)\}", yaml_content)

        # Create an ordered dictionary with the placeholders as keys and "string" as the value
        json_dict = OrderedDict()
        json_dict["no"] = "1"  # Add no: "1" as the first key-value pair
        for placeholder in placeholders:
            json_dict[placeholder] = ""

        # Wrap the dictionary under the key "1"
        final_json = {"1": json_dict}

        # Convert the dictionary to a JSON string
        updated_json_data = update_json_data_with_text_info(final_json, text_info)
        
        # Print the JSON string
        print(updated_json_data)
        return updated_json_data
    else:
        # Return an empty JSON object if the file does not exist
        print({})
        return {}
    

