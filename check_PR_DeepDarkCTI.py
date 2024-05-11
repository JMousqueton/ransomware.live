#!/usr/bin/env python3
"""
Script Name: check_PR_DarkFeedCTI.py
Description: This script monitors GitHub pull requests for changes to a specific file in a specific repository.
             It reads the last processed pull request number from a local configuration file, fetches new pull requests,
             and sends email notifications if new pull requests have been made that update the specified file.
             This script is intended to be run as a scheduled task or manually from the command line.

Author: Julien Mousqueton (julien@mousqueton.io)
Maintainer: Julien Mousqueton (julien@mousqueton.io)
Created: 2024-05-10
Last Updated: 2024-05-11

Usage:
    python check_PR_DarkFeedCTI.py [options]

Options:
    -r, --reset    Reset the configuration file to start tracking from scratch.
    -D, --Debug    Run in debug mode where emails will not be sent.
    -l, --last     Display the last high number from the config file and exit.

Dependencies:
    requests, python-dotenv, smtplib, email.mime

Example:
    python check_PR_DarkFeedCTI.py --Debug
    python check_PR_DarkFeedCTI.py --last
    python check_PR_DarkFeedCTI.py --reset

"""

import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sharedutils import stdlog, errlog
import os
from dotenv import load_dotenv
import sys
import argparse

# Define global variables at the top of the script for easy access and modification
owner = 'fastfire'
repo = 'deepdarkCTI'
file_path = 'ransomware_gang.md'
config_file = 'checkDarkFeed.cfg'

# Load environment variables once and store them in global variables
load_dotenv()
to_email = os.getenv('EMAIL_TO')
from_email = os.getenv('EMAIL_FROM')
access_token = os.getenv('GITHUB_TOKEN')
debug_mode = None  # This will be set based on command line arguments later

def check_env_vars(*vars):
    """Check environment variables and exit if any are missing or empty."""
    missing_vars = [var for var in vars if not os.getenv(var)]
    if missing_vars:
        errlog(f"Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

def send_email(subject, body):
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'localhost')
        smtp_port = int(os.getenv('SMTP_PORT', 25))
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        errlog(f"Failed to send email: {e}")

def read_last_high_number():
    try:
        with open(config_file, 'r') as file:
            last_high_number = int(file.read().strip())
        return last_high_number
    except FileNotFoundError:
        stdlog("No existing tracking file, starting fresh.")
        return 0
    except ValueError:
        stdlog("File is corrupted or empty, starting fresh.")
        return 0

def update_high_number(high_number):
    with open(config_file, 'w') as file:
        file.write(str(high_number))

def get_pull_requests():
    last_high_number = read_last_high_number()
    url = f"https://api.github.com/search/issues"
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    query = f"repo:{owner}/{repo} type:pr in:path {file_path}"
    params = {"q": query}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            prs = response.json()['items']
            current_high_number = last_high_number
            prs = sorted(prs, key=lambda pr: pr['number'])
            stdlog('Last PR checked : ' + str(current_high_number))
            email_body = ""
            for pr in prs:
                pr_number = pr['number']
                if pr_number > current_high_number:
                    current_high_number = pr_number
                    pr_details = f"PR #{pr['number']} - {pr['title']} by {pr['user']['login']} on {datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ').date()} - {pr['html_url']}\n"
                    email_body += pr_details
                    stdlog(pr_details.replace('\n',''))
            if current_high_number > last_high_number:
                stdlog('Updading ' + config_file + ' to ' + str(current_high_number))
                update_high_number(current_high_number)
                if email_body and  not debug_mode:
                    stdlog('Sending email to '+ to_email + ' ...')
                    send_email("New Ransomware Group(s) Detected", email_body)
                elif email_body and debug_mode:
                    stdlog('Debug mode activated no mail sent')
            else:
                stdlog('No new PR detected')
        else:
            errlog(f"Failed to fetch PRs with error : {response.status_code}")
    except Exception as e:
        errlog(f"Error fetching pull requests: {e}")

# Main 

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

# Environment variable checks
check_env_vars('EMAIL_TO', 'EMAIL_FROM', 'GITHUB_TOKEN')

# Argument parser setup
parser = argparse.ArgumentParser(description="Track GitHub pull requests for changes.")
parser.add_argument('-r', '--reset', action='store_true', help='Reset the configuration file.')
parser.add_argument('-D', '--Debug', action='store_true', help='Disable email sending for debugging.')
parser.add_argument('-l', '--last', action='store_true', help='Display the last PR checked presents in the config file.')

# Parse arguments
args = parser.parse_args()
debug_mode = args.Debug

if args.reset:
    stdlog('(!) Reseting configuration file')
    update_high_number(0)

if args.last:
    last_high_number = read_last_high_number()
    stdlog(f"The last PR checked is : {last_high_number}")
    sys.exit(0)

get_pull_requests()
