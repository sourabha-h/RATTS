import xml.etree.ElementTree as ET
import json
import os
import glob

def responseData():
    # Check if the XML file exists  
    # Get the path four levels up from the current file
    path_four_levels_up = os.path.join(os.path.dirname(__file__), '..', '..', '..')

    # Convert to an absolute path
    absolute_path = os.path.abspath(path_four_levels_up)
    outputxml_path = os.path.join(absolute_path,'RATTS', 'backend', 'Output','Metrics','Result', 'output.xml')
    if not os.path.exists(outputxml_path):
        raise FileNotFoundError("The file 'output.xml' does not exist.")
    matrics_path = os.path.join(absolute_path,'RATTS', 'backend', 'Output','Metrics','Result')
    # Load and parse the XML file
    tree = ET.parse(outputxml_path)
    root = tree.getroot()

    # Find the <stat> element within the <total> section
    stat_element = root.find('.//total/stat')

    # Find the status element within the test element where status is "FAIL"
    error_element = root.find('.//test/status[@status="FAIL"]')

    # Extract the values of pass and fail attributes
    pass_value = int(stat_element.get('pass'))
    fail_value = int(stat_element.get('fail'))

    # Calculate the total value
    total_value = pass_value + fail_value

    # Print the values
    print(f"Pass: {pass_value} \nFail: {fail_value} \nTotal: {total_value}")
    if(total_value == 1):
        if error_element is not None:
            print(f'Description: {error_element.text}')
            description = error_element.text
        else:
            description = ""
            print('No FAIL status found')
    else:
        description = ""

    # Check if the folder is empty
    if not os.listdir(matrics_path):
        print("The folder is empty.")
        filename=""

    else:
        # Get a list of all files in the folder that start with "matrics"
        files = glob.glob(os.path.join(matrics_path, 'metrics-*'))
        #print(f"Files found: {files}")

        # Find the latest file based on modification time
        latest_file = max(files, key=os.path.getmtime)

        # Fetch the filename
        filename = os.path.basename(latest_file)

        print(f"The latest file is: {filename}")

    data = {
        "Suite": {
            "TotalSuite": total_value,
            "TotalPassed": pass_value,
            "TotalFailed": fail_value,
            "ErrorDescription":description,
            "MetricsFileName":filename
        }
    }

    # Print the JSON data in terminal
    json_data = json.dumps(data, indent=4)
    print(json_data)
    return json_data

#responseData()



