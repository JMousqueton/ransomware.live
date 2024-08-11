#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Backup posts, groups and press json files 

__author__ = "Julien Mousqueton"
__copyright__ = "Copyright 2024, Ransomwarelive NG Project"
__version__ = "1.0.1"
# Import necessary modules
import os
import gzip
import shutil
import datetime
import difflib
import logging
#from pprint import pprint

# Backup destination
base_backup_dir = "/root/backup"
# Log File (future use)
log_file = "/var/log/backup.log"  # Specify the path to your log file
# Enable or disable gzip compression for .diff files
use_gzip = True  # Set to True to enable gzip compression
# List of files to back up
files = ["./data/victims.json", "./data/groups.json", "./data/press.json", "./data/hudsonrock.json", "/etc/nginx/sites-enabled/ransomware.conf"]


# Configure logging
logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO
)

# Define custom logging functions
def stdlog(msg):
    '''Standard info logging'''
    logging.info(msg)

def dbglog(msg):
    '''Debug logging'''
    logging.debug(msg)

def errlog(msg):
    '''Error logging'''
    logging.error(msg)

# Function to log messages with timestamps
def writelog(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} {message}\n")

# Calculate the week number
week_number = datetime.datetime.now().strftime("%Y-%U")

# Log the start of the backup process
stdlog("Backup started for week " + week_number)

# Create the week-specific backup directory
backup_dir = os.path.join(base_backup_dir, week_number)
try:
    os.makedirs(backup_dir, exist_ok=True)
    stdlog("Backup directory created: " + backup_dir)
except Exception as e:
    errlog("Failed to create backup directory " + backup_dir)
    exit(1)

# Loop through the list of files to back up
for file in files:
    # Check if the source file exists
    if not os.path.exists(file):
        errlog("Source file does not exist: " + file)
        continue  # Skip this file and proceed to the next one

    backup_file = os.path.join(backup_dir, f"{file}.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.diff")

    # Compare the current file with the backup (if it exists)
    if os.path.isfile(os.path.join(backup_dir, file)):
        with open(os.path.join(backup_dir, file), "r") as f1:
            l1 = f1.readlines()
        with open(file, "r") as f2:
            l2 = f2.readlines()
        differ = difflib.unified_diff(l1, l2, lineterm='')

        # Write the differences to the diff file
        with open(backup_file, "w") as backup_output:
            backup_output.writelines(differ)

        stdlog("Check for incremental for " + file)

        # Check if the diff file size is 0 and delete it if so
        if os.path.getsize(backup_file) == 0:
            os.remove(backup_file)
            stdlog("No incremental for " + file)
        else:
            stdlog("Creating " + backup_file)
            # If use_gzip is True, gzip the .diff file
            if use_gzip:
                try:
                    with open(backup_file, "rb") as f_in, gzip.open(backup_file + ".gz", "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                    os.remove(backup_file)  # Remove the original .diff file
                    stdlog("Gzipped incremental file: " + backup_file + ".gz")
                except Exception as e:
                    errlog("Failed to gzip incremental file: " + backup_file)
    else:
        try:
            shutil.copyfile(file, os.path.join(backup_dir, file))
            stdlog("Created new backup for week " + week_number + ": " + file)
        except Exception as e:
            errlog("Failed to create new backup for week " + week_number + ": " + file)

# Log the completion of the backup process for the current week
stdlog("Backup completed for week " + week_number)
