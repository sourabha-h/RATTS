import os
import glob

# Specify the folder path
folder_path = 'Output/Metrics'

# Check if the folder is empty
if not os.listdir(folder_path):
    print("The folder is empty.")
else:
    # Get a list of all files in the folder that start with "matrics"
    files = glob.glob(os.path.join(folder_path, 'metrics-*'))

    # Debugging: Print the list of files found
    print(f"Files found: {files}")

    if not files:
        print("No files with the prefix 'matrics' found.")
    else:
        try:
            # Find the latest file based on modification time
            latest_file = max(files, key=os.path.getmtime)

            # Fetch the filename
            filename = os.path.basename(latest_file)

            print(f"The latest file is: {filename}")
        except ValueError:
            print("Error: No files found to process.")
