#!/usr/bin/env python3
from pathlib import Path
from dotenv import load_dotenv
import json, os
import argparse
from shared_utils import stdlog, errlog, openjson, grouptobluesky
import tldextract
from PIL import Image, ImageFilter  # Required for the blur functionality
import asyncio
import hudsonrockapi
import time
from datetime import datetime
import validators
import glob

# Load environment variables from ../.env
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
# Paths from environment variables
home = os.getenv("RANSOMWARELIVE_HOME")
db_dir = Path(home + os.getenv("DB_DIR"))
GROUPS_FILE = db_dir / "groups.json"

def checkexisting(provider):
    '''
    check if group already exists within groups.json
    '''
    groups = openjson(GROUPS_FILE)
    for group in groups:
        if group['name'] == provider:
            return True
    return False

def creategroup(name, location):
    '''
    create a new group for a new provider - added to groups.json
    '''
    # Get the current date and time
    current_date = datetime.now()
    # Format the date as YYYY-MM-DD
    now = current_date.strftime('%Y-%m-%d')
    location = siteschema(location)
    insertdata = {
        'name': name,
        'date': now,
        'meta': None,
        'description': None,
        'contact': None,
        'locations': [
            location
        ],
        'profile': list()
    }
    return insertdata

def getapex(slug):
    '''
    returns the domain for a given webpage/url slug
    '''
    stripurl = tldextract.extract(slug)
    if stripurl.subdomain:
        return stripurl.subdomain + '.' + stripurl.domain + '.' + stripurl.suffix
    return stripurl.domain + '.' + stripurl.suffix


def siteschema(location):
    '''
    returns a dict with the site schema
    '''
    # Validate if location is a valid URL
    if not validators.url(location):
        stdlog(f"Warning: Invalid URL format detected for '{location}'. Assuming it's an FQDN.")
        location = 'http://' + location  # Fallback for non-URL inputs

    schema = {
        'fqdn': getapex(location),
        'title': None,
        'slug': location,
        'available': False,
        'updated': None,
        'lastscrape': '2021-01-01 00:00:00.000000',
        'enabled': True,
        'type': 'DLS'
    }
    return schema



def write_to_file(data, file_path):
    """
    Utility function to write JSON data to a file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        errlog(f"Failed to write to {file_path}: {e}")

def siteappender(name, location):
    """
    Append a new location to an existing group in groups.json.
    """
    lock_file_path = Path(home + '/tmp/scrape.lock')  # Update with your actual lock file path
    wait_for_lock(lock_file_path)  # Wait for the lock to disappear
    
    groups = openjson(GROUPS_FILE)
    success = False
    for group in groups:
        if group['name'] == name:
            if siteschema(location) not in group['locations']:
                group['locations'].append(siteschema(location))
                success = True
            break

    if success:
        write_to_file(groups, GROUPS_FILE)
        stdlog(f"Ransomware.live: Appended location to group '{name}'.")
    else:
        errlog(f"Ransomware.live: Group '{name}' does not exist. Cannot append location.")

def wait_for_lock(lock_file_path, check_interval=5):
    """
    Waits until the specified lock file no longer exists.
    
    :param lock_file_path: Path to the lock file.
    :param check_interval: Time in seconds to wait between checks.
    """
    while Path(lock_file_path).exists():
        stdlog(f"Waiting for lock file '{lock_file_path}' to be released...")
        time.sleep(check_interval)
    stdlog(f"Lock file '{lock_file_path}' has been released. Proceeding...")

def siteadder(name, location):
    """
    Add a new group to groups.json or append to an existing group.
    """
    lock_file_path = Path(home + '/tmp/scrape.lock')  # Update with your actual lock file path
    wait_for_lock(lock_file_path)  # Wait for the lock to disappear
    if checkexisting(name):
        stdlog(f"Ransomware.live: Group '{name}' already exists. Appending location instead.")
        siteappender(name, location)
    else:
        groups = openjson(GROUPS_FILE)
        new_group = creategroup(name, location)
        groups.append(new_group)
        write_to_file(groups, GROUPS_FILE)
        grouptobluesky(name)
        stdlog(f"Ransomware.live: Added new group '{name}' to the database.")

def blur_image(input_path, output_path, blur_radius=5):
    try:
        # Open the input image
        img = Image.open(input_path)
        
        # Apply Gaussian blur with the specified radius
        blurred_img = img.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # Get the directory and filename from the input path
        directory, filename = os.path.split(output_path)
        
        # Generate the new path for the blurred image
        output_path = os.path.join(directory,filename)
        
        # Save the blurred image to the output path
        blurred_img.save(output_path)
        
        stdlog(f"Image blurred successfully")
    except Exception as e:
        errlog(f"An error occurred: {e}")

def rename_original_image(input_path):
    try:
        # Get the directory and filename from the input path
        directory, filename = os.path.split(input_path)
        
        # Generate the new name for the original image
        new_name = os.path.splitext(filename)[0] + "-ORIG.png"
        
        # Create the new path for the renamed original image
        new_path = os.path.join(directory, new_name)
        
        # Rename the original image
        os.rename(input_path, new_path)
        
        stdlog(f"Original image renamed to {new_name}")
        return new_path
    except Exception as e:
        errlog(f"An error occurred while renaming the original image: {e}")
        return None

def purge_old_html_files():
    """
    Deletes all *.html files in tmp_dir older than 24 hours.
    """
    tmp_dir = Path(home + '/tmp')  # Adjust based on actual usage
    if not tmp_dir.exists():
        errlog(f"Directory '{tmp_dir}' does not exist. Skipping purge.")
        return

    cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago
    deleted_files = 0

    for file in tmp_dir.glob("*.html"):
        if file.stat().st_mtime < cutoff_time:
            try:
                file.unlink()  # Delete file
                deleted_files += 1
            except Exception as e:
                errlog(f"Failed to delete {file}: {e}")

    stdlog(f"Purged {deleted_files} old HTML files from {tmp_dir}.")

def main():
    print(
    r'''
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

    parser = argparse.ArgumentParser(description="Manage Ransomware.live.")
    group = parser.add_mutually_exclusive_group(required=True)

    # Adding options
    group.add_argument(
        '-U', '--append',
        nargs=2,
        metavar=('NAME', 'LOCATION'),
        help="Append a new location to an existing group."
    )
    group.add_argument(
        '-A', '--add',
        nargs=2,
        metavar=('NAME', 'LOCATION'),
        help="Add a new group or append a location to an existing group."
    )
    group.add_argument(
        '-B', '--blur',
        metavar='PATH',
        help="Apply a blur effect to the specified image file."
    )
    group.add_argument(
        '-I', '--infostealer',
        metavar='DOMAIN',
        help="Perform an infostealer query for the specified domain."
    )
    group.add_argument(
        '-P', '--purge',
        action='store_true',
        help="Delete all *.html files in tmp_dir older than 24h."
)

    args = parser.parse_args()


    # Handling options
    if args.append:
        name, location = args.append
        siteappender(name, location)
    elif args.add:
        name, location = args.add
        siteadder(name, location)
    elif args.blur:
        renamed_input_path = rename_original_image(args.blur)
        if renamed_input_path:
            blur_image(renamed_input_path, args.blur)
    elif args.infostealer:
        asyncio.run(hudsonrockapi.run_query(args.infostealer))
    if args.purge:
        purge_old_html_files()

if __name__ == "__main__":
    main()
