import os
import re
import json
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telethon import TelegramClient, events
from urllib.parse import urlparse
import requests

# Load environment variables from .env file
load_dotenv()

api_id = os.getenv('T_API_ID')
api_hash = os.getenv('T_API_HASH')
phone_number = os.getenv('T_PHONE_NUMBER')
json_file_path = './data/hudsonrock.json'
timer = 300  # Global timer variable in seconds

# Create the client and connect
client = TelegramClient('session_name', api_id, api_hash)

def extract_figures(message):
    figures = {
        'Compromised Employees': 0,
        'Compromised Users': 0,
        'Employee URLs': 0,
        'User URLs': 0,
        'Third Party Domains': 0,
        'Compromised Third Party Employees': 0
    }
    
    patterns = {
        'Compromised Employees': r'Compromised Employees:\s(\d+)',
        'Compromised Users': r'Compromised Users:\s(\d+)',
        'Employee URLs': r'Employee URLs:\s(\d+)',
        'User URLs': r'User URLs:\s(\d+)',
        'Third Party Domains': r'Third Party Domains:\s(\d+)',
        'Compromised Third Party Employees': r'Compromised Third Party Employees:\s(\d+)'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, message)
        if match:
            figures[key] = int(match.group(1))

    return figures

def load_json_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}

def load_json_file(filepath):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_json_file(data, filepath):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def update_json_file(domain, figures):
    data = load_json_file(json_file_path)

    if domain not in data:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data[domain] = {
            "update": now,
            "employees": figures['Compromised Employees'],
            "users": figures['Compromised Users'],
            "thirdparties_domain": figures['Third Party Domains'],
            "employees_url": figures['Employee URLs'],
            "users_url": figures['User URLs'],
            "thirdparties": figures['Compromised Third Party Employees']
        }

        save_json_file(data, json_file_path)
        print(f"Added new entry for {domain} to {json_file_path}.")
    else:
        print(f"{domain} is already present in {json_file_path}.")

async def query_telegram(domain):
    await client.send_message('@HudsonRockBot', domain)

    @client.on(events.NewMessage(chats='@HudsonRockBot'))
    async def handler(event):
        message_text = event.message.message
        figures = extract_figures(message_text)
        update_json_file(domain, figures)
        client.remove_event_handler(handler)  # Remove handler after processing

async def process_posts():
    # Load the posts data
    posts_data = load_json_url('https://raw.githubusercontent.com/Casualtek/Cyberwatch/main/cyberattacks.json')

    # Get the current date
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1

    for post in posts_data:
        date_str = post.get('date', '')
        domain = post.get('domain', '')

        try:
            post_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            continue  # Skip if date format is incorrect

        # Process only posts from the current year and month or the last month
        if (post_date.year == current_year and post_date.month >= last_month) or \
           (post_date.year == last_month_year and post_date.month == last_month):
            if domain:
                data = load_json_file(json_file_path)
                if domain not in data:
                    print(f'Quering {domain} for infostealer')
                    await query_telegram(domain)
                    await asyncio.sleep(timer)  # Sleep for the specified timer duration
                else:
                    print(f"{domain} is already present in {json_file_path}.")

async def main():
    # Start the client
    await client.start(phone_number)
    await process_posts()
    await client.disconnect()

# Start the main function
with client:
    client.loop.run_until_complete(main())
