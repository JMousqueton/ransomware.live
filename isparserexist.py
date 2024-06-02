import os
import json
import shutil
import sys
from datetime import datetime
from sharedutils import stdlog, errlog

"""
This script checks if parser files exist for each group listed in a JSON file and updates the JSON file with the results.
If any changes are made to the JSON file, it creates a backup of the original file before saving the updated version.

Functions:
- check_parser_file_exists(location_name): Checks if a parser file exists for the given location name.

Main Process:
1. Reads the "groups.json" file.
2. Iterates through each group, checking if the corresponding parser file exists.
3. If the parser status has changed, updates the group entry and logs the change.
4. If any changes were made, creates a backup of the original "groups.json" file.
5. Writes the updated data back to "groups.json".
6. Handles errors such as missing files or invalid JSON, and logs appropriate messages.

Logging:
- Uses stdlog for informational messages.
- Uses errlog for error messages.

Backup:
- Creates a backup copy of the original JSON file only if changes were made.
- The backup filename includes the current date to ensure uniqueness.
"""

def check_parser_file_exists(location_name):
    lowercase_name = location_name.lower()
    file_path_1 = os.path.join("parsers", f"{lowercase_name}.py")
    file_path_2 = os.path.join("parsers", f"{lowercase_name}-api.py")
    return os.path.exists(file_path_1) or os.path.exists(file_path_2)

def main():
    file_path = "groups.json"
    
    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        groups_with_changes = False
        for item in data:
            group_name = item["name"]
            parser_exists = check_parser_file_exists(group_name)

            if item["parser"] != parser_exists:
                item["parser"] = parser_exists
                stdlog("Changed 'parser' for group '" + group_name + "' to " + str(parser_exists))
                groups_with_changes = True

        # Make a backup copy of the original JSON file only if changes were made
        if groups_with_changes:
            current_date = datetime.now()
            backup_filename = file_path + '.' + current_date.strftime("%Y-%m-%d")
            try:
                shutil.copy(file_path, backup_filename)
                stdlog("Backup of the original JSON file created as: " + backup_filename)
            except Exception as e:
                errlog("An error occurred while creating the backup file: " + str(e))
                sys.exit(1)

        #with open(file_path, "w") as json_file:
        #    json.dump(data, json_file, indent=4)
        
        stdlog("Check completed and groups.json updated.")
    
    except FileNotFoundError:
        errlog("Error: groups.json file not found.")
    except json.JSONDecodeError:
        errlog("Error: groups.json file is not a valid JSON.")
    except Exception as e:
        errlog("An unexpected error occurred: " + str(e))

if __name__ == "__main__":
    print(
    '''
       _______________                        |*\_/*|________
      |  ___________  |                      ||_/-\_|______  |
      | |           | |                      | |           | |
      | |   0   0   | |                      | |   0   0   | |
      | |     -     | |                      | |     -     | |
      | |   \___/   | |                      | |   \___/   | |
      | |___     ___| |                      | |___________| |
      |_____|\_/|_____|                      |_______________|
        _|__|/ \|_|_.............💔.............._|________|_
       / ********** \                          / ********** \ 
     /  ************  \   ransomware.live     /  ************  \ 
    --------------------                    --------------------
    '''
    )
    main()