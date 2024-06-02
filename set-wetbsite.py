import json
from datetime import datetime, timedelta

# Function to check if a given date string is for today or yesterday
def is_today_or_yesterday(date_str):
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    # Parse the date string to a datetime object
    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f').date()
    
    # Check if the date is either today or yesterday
    return date_obj == today or date_obj == yesterday

# Function to read, filter, and update the JSON data for website entries
def update_entries_with_website_for_recent_discoveries(file_path):
    # Open the JSON file and load the data
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Iterate over each entry in the data
    for entry in data:
        discovered_date = entry.get('discovered', '')
        
        # Proceed only if the 'discovered' date is today or yesterday
        if discovered_date and is_today_or_yesterday(discovered_date):
            # Check if the 'website' field is empty or missing
            if not entry.get('website'):
                # Prompt the user for a website URL
                print(f"Entry: {entry.get('post_title', 'No title available')}")
                new_website = input("This entry has no website set. Please enter a website URL or XX to pass: ")

                # Update the entry with the new website if it's not 'XX'
                if new_website.strip() and new_website.upper() != 'XX':
                    entry['website'] = new_website.strip()

    # Write the updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Path to your JSON file
file_path = './posts.json'

# Call the function to update website entries for recent discoveries
print("Starting the website update process for recent discoveries...")
update_entries_with_website_for_recent_discoveries(file_path)
print("Update process completed.")

