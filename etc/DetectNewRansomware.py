#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# A script to detect new ransomware blog from fastfire/deepdarkCTI repository 
# Send an email with a screenshot 
##

__author__ = "Julien Mousqueton"
__copyright__ = "Copyright 2023, Ransomware.live Project"
__version__ = "1.0.0"

# Import necessary modules
import requests
import re
import json
import sys
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import os


# For screenshot 
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os, hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from ransomwarelive import stdlog, dbglog, errlog


# mail 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

import secrets
import string

def generate_random_string(length=8):
    letters = string.ascii_letters
    random_string = ''.join(secrets.choice(letters) for _ in range(length))
    return random_string

def send_email(subject, body, to_email, attachment_path=None):
    # Set up the SMTP server
    smtp_server = 'localhost'
    smtp_port = 25
    smtp_tls =  False
    smtp_username = ''
    smtp_password = ''

    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = "noreply@ransomware.live"
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body text
    msg.attach(MIMEText(body, 'plain'))

    # Attach the image if specified
    if attachment_path:
        attachment = open(attachment_path, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % attachment_path)
        msg.attach(part)

    # Connect to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    if smtp_tls:
        server.starttls()
        server.login(smtp_username, smtp_password)

    # Send the email
    server.sendmail(smtp_username, to_email, msg.as_string())

    # Quit the server
    server.quit()
    stdlog('Mail sent')

# Example usage:
#subject = 'Test Email with Attachment'
#body = 'This is a test email with an attachment.'
#to_email = 'recipient@example.com'
#attachment_path = 'path/to/your/image.jpg'  # Replace with the actual path to your image
#
#send_email(subject, body, to_email, attachment_path)



def screenshot(webpage,delay=15000,output=None):
    stdlog('screenshot : {}'.format(webpage))
    name = '/tmp/' + output + '.png'
    with sync_playwright() as play:
                try:
                    browser = play.chromium.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                            args=[''])
                    context = browser.new_context(ignore_https_errors= True )
                    page = context.new_page()
                    page.goto(webpage, wait_until='load', timeout = 120000)
                    page.bring_to_front()
                    page.wait_for_timeout(delay)
                    page.mouse.move(x=500, y=400)
                    page.wait_for_load_state('networkidle')
                    page.mouse.wheel(delta_y=2000, delta_x=0)
                    page.wait_for_load_state('networkidle')
                    page.wait_for_timeout(12000)
                    page.screenshot(path=name, full_page=True)
                except PlaywrightTimeoutError:
                    stdlog('Timeout!')
                except Exception as exception:
                    stdlog(exception)
                #browser.close()




# Function to extract .onion URLs from Markdown content
def extract_onion_urls(md_content):
    pattern = re.compile(r'(http[s]?://[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]+\.onion)')
    return re.findall(pattern, md_content)

# Function to check if URL is in groups.json or online and not excluded
def check_url(url, group_data, tor_proxy, exclusions_file):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    onion_url_no_protocol = domain.split("://")[-1] if "://" in domain else domain

    # Check if the URL is in the exclusions file
    with open(exclusions_file, 'r') as exclusions:
        if onion_url_no_protocol in exclusions.read():
            # print(f"{url} is excluded according to {exclusions_file}")
            return

    # Check if the URL is in groups.json
    for group_entry in group_data:
        for location in group_entry.get("locations", []):
            if domain == location["fqdn"]:
                #print(f"{url} is present in groups.json for group: {group_entry['name']}")
                return

    # Check if the URL is online via Tor proxy
    try:
    #    response = requests.get(url, timeout=5, proxies={'http': tor_proxy, 'https': tor_proxy})
    #    if response.status_code == 200:
            stdlog('New Ransomware Site found : ' +  url)
            random_string = generate_random_string()
            screenshot(url,delay=15000,output=random_string)
            body="A new ransomware site has been detected : \n\n"+url 
            file="/tmp/"+random_string+".png" 
            if os.path.exists(file):
                send_email("New Ransomware site detected",body, " support@ransomwarelive.freshdesk.com",file)
            else:
                send_email("New Ransomware site detected",body, " support@ransomwarelive.freshdesk.com")
    #    else:
    #        print(f"{url} is not online (HTTP Status Code: {response.status_code})")
    except requests.ConnectionError:
        print(f"{url} is not online (Connection Error)")



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
    stdlog('Analyze deepdarkCTI repository')
    # URL of the Markdown file
    md_url = "https://raw.githubusercontent.com/fastfire/deepdarkCTI/main/ransomware_gang.md"

    # Fetching content of the Markdown file
    response = requests.get(md_url)
    md_content = response.text

    # Load groups.json data
    with open('../data/groups.json') as json_file:
        group_data = json.load(json_file)

    # Set up Tor proxy
    tor_proxy = 'socks5h://127.0.0.1:9050'  # Make sure Tor is running on port 9050

    # Exclusions file
    exclusions_file = './sources.exclusions'

    # Extract .onion URLs from Markdown content
    onion_urls = extract_onion_urls(md_content)

    # Check each .onion URL
    for onion_url in onion_urls:
        check_url(onion_url, group_data, tor_proxy, exclusions_file)
    stdlog('Analyze finished')
    
    stdlog('Analyze CTI.FYI repository')
    # URL to fetch HTML content from
    url = "https://cti.fyi/"

    # Fetch the HTML content
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all rows in the table body
    rows = soup.select('table.style-table tbody tr')

    # Extract URLs where the next <td> is &#x1F7E2;
    urls = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 1 and '🟢' in cols[1].get_text():
            code_tag = row.find('code')
            if code_tag:
                url = code_tag.get_text()
                if url != "http://bl@ckt0r:bl@ckt0r@bl4cktorpms2gybrcyt52aakcxt6yn37byb65uama5cimhifcscnqkid.onion/0x00/data-breach.html":
                    check_url(url, group_data, tor_proxy, exclusions_file)
                
    stdlog('Analyze finished')
                
