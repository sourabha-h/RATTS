import os
def clearLogFiles():
    # Path to the folder
    #folder_path = r'c:\\xampp\\htdocs\\RATTS\\backend\\Output\\Metrics\\Result\\'
    path_four_levels_up = os.path.join(os.path.dirname(__file__), '..', '..')
    absolute_path = os.path.abspath(path_four_levels_up)
    folder_path = os.path.join(absolute_path,'backend', 'Output', 'Metrics', 'Result')
    # List of file names to delete
    print(f"The absolute_path is: {absolute_path}")
    print(f"The resource_path is: {folder_path}")
    files_to_delete = ['log.html', 'output.xml', 'report.html']
    
    for filename in files_to_delete:
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove the file
                print(f'Successfully deleted {file_path}')
            else:
                print(f'{file_path} is not a file or does not exist')
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    
    #folder_path1 = r'c:\\xampp\\htdocs\\RATTS\\backend\\Output\\result\\'
    folder_path1 = os.path.join(absolute_path,'backend', 'Output', 'Metrics','Result')
    for filename in os.listdir(folder_path1):
        file_path = os.path.join(folder_path1, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            else:
                print(f'{file_path} is not a file or does not exist')
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')