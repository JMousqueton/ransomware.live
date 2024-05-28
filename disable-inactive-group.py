import json
from datetime import datetime
import shutil
import os
import sys
from sharedutils import stdlog, errlog  

"""
Script to update 'groups.json' file

This script performs the following tasks:
1. Loads the 'groups.json' file.
2. Determines the previous year based on the current month:
   - If the current month is greater than 3, it uses the previous year.
   - Otherwise, it uses two years prior.
3. Counts and prints the number of enabled locations before any changes are made.
4. Checks each location in the JSON data to see if the 'lastscrape' date is in the calculated previous year and if 'enabled' is true.
5. Updates the 'enabled' field to false if the conditions are met and tracks the groups with changes.
6. Counts and prints the number of enabled locations after the changes are made.
7. Creates a backup of the original 'groups.json' file with the current date appended to the filename.
8. Saves the updated JSON data back to the original 'groups.json' file.
"""

# Function to check if the lastscrape date is in the previous year
def is_last_scrape_in_previous_year(date_str, previous_year):
    try:
        date = datetime.fromisoformat(date_str)
        return date.year == previous_year
    except ValueError:
        return False

# Count the number of enabled locations
def count_enabled_locations(data):
    count = 0
    for group in data:
        for location in group['locations']:
            if location['enabled']:
                count += 1
    return count

# Load the JSON file with error handling
def load_json_file(file_path):
    if not os.path.exists(file_path):
        errlog("Error: File '" + file_path + "' not found.")
        return None
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except json.JSONDecodeError as e:
        errlog("Error decoding JSON: " + str(e))
        return None
    except Exception as e:
        errlog("An error occurred while reading the file: " + str(e))
        return None

# Save the updated JSON data to the original file with error handling
def save_json_file(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        stdlog("Updated " + file_path + " file saved.")
    except Exception as e:
        errlog("An error occurred while writing the file: " + str(e))

# Main script logic
def main():
    file_path = 'groups.json'
    data = load_json_file(file_path)
    if data is None:
        return
    
    # Get the previous year based on the current month
    current_date = datetime.now()
    if current_date.month > 3:
        previous_year = current_date.year - 1
    else:
        previous_year = current_date.year - 2
    
    # Initial count of enabled locations
    initial_enabled_count = count_enabled_locations(data)

    # Track if any changes are made and print the group name
    groups_with_changes = set()

    # Process each group
    for group in data:
        for location in group['locations']:
            if is_last_scrape_in_previous_year(location['lastscrape'], previous_year) and location['enabled']:
                location['enabled'] = False
                groups_with_changes.add(group['name'])

    # Final count of enabled locations
    final_enabled_count = count_enabled_locations(data)

    # Print the names of the groups with changes
    for group_name in groups_with_changes:
        stdlog("Disable one location for group: " + group_name)

    # Print the counts of enabled locations
    stdlog("Disable any Ransomware group'slocation inactives since "+str(previous_year))
    stdlog("Initial count of enabled locations: " + str(initial_enabled_count))
    stdlog("Final count of enabled locations: " + str(final_enabled_count))

    # Make a backup copy of the original JSON file only if changes were made
    if groups_with_changes:
        backup_filename = file_path + '.' + current_date.strftime("%Y-%m-%d")
        try:
            shutil.copy(file_path, backup_filename)
            stdlog("Backup of the original JSON file created as: " + backup_filename)
        except Exception as e:
            errlog("An error occurred while creating the backup file: " + str(e))
            sys.exit(1)

        # Save the updated JSON data to the original file
        save_json_file(file_path, data)
    else:
        stdlog('No modification needed')

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
