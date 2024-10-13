import os
import re
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '/var/www/ransomware-ng/libs')))
from gpt_query import GPTQuery
from ransomwarelive import stdlog, errlog, extract_md5_from_filename, find_slug_by_md5, appender


# Load environment variables from .env file in the same directory
load_dotenv()

api_id = os.getenv('T_API_ID')
api_hash = os.getenv('T_API_HASH')
channel_username = '@StmXRaaS'  # The username of the Telegram channel
GPT = os.getenv('OPENAI_API_KEY')

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start()
    
    # Fetch the last 10 messages from the channel
    channel = await client.get_entity(channel_username)
    history = await client(GetHistoryRequest(
        peer=channel,
        limit=10,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))
    
    messages = history.messages
    for message in messages:
        full_message = message.message
        if full_message:  # Check if full_message is not empty
            # Filter out lines that start with "Tox ID:" or "Blog Link:"
            obfuscated_message = re.sub(r'\b[a-zA-Z0-9]{16}\.onion\b', '[redacted].onion', full_message)
            
            # Format the date
            date = message.date.strftime("%Y-%m-%d %H:%M:%S.%f")
            first_line = full_message.split('\n')[0] if full_message else ''
            
            if GPT: 
                gpt_query = GPTQuery()
                prompt = f'find the company name in this string "{first_line}". Write only the company name nothing else'
                victim = gpt_query.query(prompt)



            #print(f"Date: {date}")
            #print(f"Full Message: {obfuscated_message}")
            #print(f"victim: {victim}\n")
            #  def appender(post_title, group_name, description="", website="", published="", post_url="")
            appender(victim,'stormous',obfuscated_message,'',date)

# Use asyncio to run the main coroutine
with client:
    client.loop.run_until_complete(main())
