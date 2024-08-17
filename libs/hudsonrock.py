import os
import re
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient, events
import logging

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO
)

def stdlog(msg):
    logging.info(msg)

def dbglog(msg):
    logging.debug(msg)

def errlog(msg, pushover=False):
    logging.error(msg)
    load_dotenv()

def load_json_file(filepath):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_json_file(data, filepath):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def query_hudsonrock(domain_name):
    env_path = os.path.join(os.path.dirname(__file__), '../.env')
    load_dotenv(dotenv_path=env_path)

    api_id = os.getenv('T_API_ID')
    api_hash = os.getenv('T_API_HASH')
    phone_number = os.getenv('T_PHONE_NUMBER')
    json_file_path = os.getenv('DATA_DIR') + 'hudsonrock.json'
    timer = 120

    data = load_json_file(json_file_path)

    if domain_name in data:
        stdlog(f"{domain_name} is already present in the database.")
        return None

    return {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone_number": phone_number,
        "json_file_path": json_file_path,
        "timer": timer,
        "domain_name": domain_name
    }

async def query_telegram(client, domain_name, json_file_path, timer):
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

    @client.on(events.NewMessage(chats='@HudsonRockBot'))
    async def handler(event):
        message_text = event.message.message
        figures = extract_figures(message_text)
        stdlog("Extracted figures:")
        for key, value in figures.items():
            stdlog(f"{key}: {value}")

        update_json_file(domain_name, figures)

    await client.start()
    await client.send_message('@HudsonRockBot', domain_name)
    stdlog(f'Waiting for {timer} seconds to avoid being blacklisted')
    await asyncio.sleep(timer)
    await client.disconnect()

async def run_query(domain_name):
    config = query_hudsonrock(domain_name.lower())
    
    if config:
        stdlog(f'Processing {domain_name} ...')
        client = TelegramClient('session_name', config['api_id'], config['api_hash'])
        await query_telegram(client, config['domain_name'], config['json_file_path'], config['timer'])
