import xml.etree.ElementTree as ET
import json
import os
import glob

def responseData():
    #Create the relative path
    path_four_levels_up = os.path.join(os.path.dirname(__file__), '..', '..')
    absolute_path = os.path.abspath(path_four_levels_up)
    folder_path = os.path.join(absolute_path,'backend', 'Output', 'Metrics', 'Result')
    file_path = os.path.join(folder_path,'output.xml')
    
    # Check if the XML file exists    
    #if not os.path.exists(r'c:\\xampp\\htdocs\\RATTS\\backend\\Output\\Metrics\\Result\\output.xml'):
    if not os.path.exists(file_path):
        raise FileNotFoundError("The file 'output.xml' does not exist.")
    #matrics_path = r'c:\\xampp\\htdocs\\RATTS\\backend\\Output\\Metrics\\Result\\'
    matrics_path = folder_path
    # Load and parse the XML file
    #tree = ET.parse(r'c:\\xampp\\htdocs\\RATTS\\backend\\Output\\Metrics\\Result\\output.xml')
    tree = ET.parse(file_path)
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
        #files = glob.glob(os.path.join(matrics_path, 'metrics-*'))
        #print(f"Files found: {files}")

        # Find the latest file based on modification time
        #latest_file = max(files, key=os.path.getmtime)

        # Fetch the filename
        #filename = os.path.basename(latest_file)

        #print(f"The latest file is: {filename}")


        # Get a list of all directories in the specified path
        folders = [f for f in glob.glob(matrics_path + "/*") if os.path.isdir(f)]
        # Get the folder with the latest creation time
        latest_folder_path = max(folders, key=os.path.getctime)
        # Get only the folder name
        latest_folder_name=os.path.basename(latest_folder_path)
        print(f"The latest folder is: {latest_folder_name}")

        filename = f"{latest_folder_name}\metrics-{latest_folder_name}.html"
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

    # List of specific files to delete
    files_to_delete = ['log.html', 'output.xml','report.html']

    # Delete specific files
    for file in files_to_delete:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"File '{file_path}' deleted successfully!")
            except Exception as e:
                print(f"Error deleting file '{file_path}': {e}")

    # Find and delete files that start with 'metrics'
    metrics_files_to_delete = glob.glob(os.path.join(folder_path, 'metrics*'))

    for file in metrics_files_to_delete:
        if os.path.isfile(file):
            try:
                os.remove(file)
                print(f"File '{file}' deleted successfully!")
            except Exception as e:
                print(f"Error deleting file '{file}': {e}")

    return json_data


#responseData()



