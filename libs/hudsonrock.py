import os
import re
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient, events
from urllib.parse import urlparse

def query_hudsonrock(domain_name):
    from ransomwarelive import stdlog
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(__file__), '../.env')
    load_dotenv(dotenv_path=env_path)

    api_id = os.getenv('T_API_ID')
    api_hash = os.getenv('T_API_HASH')
    phone_number = os.getenv('T_PHONE_NUMBER')
    json_file_path = os.getenv('DATA_DIR') + 'hudsonrock.json'
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
        
            

    async def query_telegram(domain):
        await client.send_message('@HudsonRockBot', domain)

        @client.on(events.NewMessage(chats='@HudsonRockBot'))
        async def handler(event):
            message_text = event.message.message
            # print(f"Received message: {message_text}")

            figures = extract_figures(message_text)
            stdlog("Extracted figures:")
            for key, value in figures.items():
                stdlog(f"{key}: {value}")

            # Update the JSON file
            update_json_file(domain, figures)

    async def main(domain):
        # Start the client
        await client.start(phone_number)
        await query_telegram(domain)
        stdlog(f'Waiting for {timer}ms to avoid being blacklisted')
        await asyncio.sleep(timer)  # Sleep for the specified timer duration
        await client.disconnect()

    # Start the main function
    data = load_json_file(json_file_path)
    if domain_name not in data:
        with client:
            client.loop.run_until_complete(main(domain_name))
    else:
        stdlog(f"{domain_name} is already present in the database.")
