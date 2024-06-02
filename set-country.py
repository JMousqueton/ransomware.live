import json
from datetime import datetime
import re  # Import the regular expression module
import pycountry  # Import pycountry for country code validation

# Function to read, filter, and update the JSON data
def update_entries_with_country(file_path):
    # Open the JSON file and load the data
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Iterate over each entry in the data
    for entry in data:
        # Check if 'post_title' contains '**' and skip if it does
        if '**' in entry.get('post_title', ''):
            continue
        # Extract the 'discovered' date
        date_str = entry.get('discovered')
        # Convert the date string to a datetime object
        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')

        # Check if the year is 2024 and country is not set
        if date_obj.year == 2024 and not entry.get('country'):
            while True:
                print(f"Entry: {entry['post_title']}")
                new_country = input("This entry has no country set. Please enter a 2-letter country code or XX to pass : ")

                # Check if the input is exactly 2 letters and valid
                if re.match(r'^[a-zA-Z]{2}$', new_country):
                    country = pycountry.countries.get(alpha_2=new_country.upper())
                    if country:
                        entry['country'] = new_country.upper()  # Use the valid and formatted country code
                        break
                    elif new_country.upper() == 'XX':
                        break
                    else:                     
                        print("The country code doesn't exist. Please enter a valid 2-letter country code.")
                else:
                    print("Invalid format. Please enter a 2-letter country code.")
 # After setting the country, check and ask for website if it's empty
            if not entry.get('website'):
                new_website = input("This entry has no website set. Please enter a website URL or XX to pass: ")
                if new_website.strip() and new_website.upper() != 'XX':
                    entry['website'] = new_website.strip()  # Set the website


    # Write the updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Call the function to update entries

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
     /  ************  \     ransomwhat?      /  ************  \ 
    --------------------                    --------------------
    '''
)
file_path = './posts.json'
update_entries_with_country(file_path)
