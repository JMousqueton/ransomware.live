import json
import os
import glob

# Path to the JSON file
file_path = 'groups.json'

# Reading the file
with open(file_path, 'r') as file:
    groups = json.load(file)  # Assuming the JSON structure is a list of groups

# Iterate over each group in the JSON
for group in groups:
    # Construct the expected filename for the group's Python file within the './parsers/' directory
    expected_file = f"./parsers/{group['name']}.py"
    
    # Construct a search pattern for files beginning with the group name
    search_pattern = f"./parsers/{group['name']}*.py"
    
    # Find files that match the search pattern
    matching_files = glob.glob(search_pattern)

    # Check the 'parser' attribute and file existence based on its value
    if group['parser'] is False:
        if os.path.exists(expected_file):
            print(f"The specific file '{expected_file}' exists.")
        elif matching_files:
            print(f"Specific file '{expected_file}' does not exist, but found other matching files: ", end='')
            for f in matching_files:
                print(f"{f}")
       

    elif group['parser'] is True and not os.path.exists(expected_file) and not matching_files:
        print(f"The file '{expected_file}' and any matching files do not exist.")
