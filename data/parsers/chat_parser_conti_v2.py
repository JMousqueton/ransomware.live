#!/usr/bin/python3
import os
import sys
import json
from bs4 import BeautifulSoup

def parse_html_to_json(html_file, output_file):
    # Load the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the chat ID
    # chat_id = soup.find('h3').get_text().strip()
    chat_id = ''

    # Find all chat items
    chat       = soup.find('div', class_='messages')

    # Extract party and message details for each chat item
    messages = []
    for item in chat.children:
        if not isinstance(item, str):
            if 'user' in item['class']:
                party = 'Victim'
            elif 'support' in item['class']:
                party = 'Conti'
            else:
                continue
        
            chat_messages = item.find_all('div', class_='message')
            for chat_message in chat_messages:
                datetime_div = chat_message.find('div', class_='date')
                datetime = datetime_div['title']
                content_div = chat_message.find('div', class_='text')
                content = content_div.get_text().strip()

                message = {
                    'party': party,
                    'content': content,
                    'timestamp': datetime
                }
                messages.append(message)

    # Create the JSON object with chat ID and messages
    chat_data = {
        'chat_id': chat_id,
        'messages': messages
    }

    # Get the output file name from the input HTML file name
    output_filename = os.path.splitext(os.path.basename(html_file))[0] + '.json'
    output_path = os.path.join(output_file, output_filename)

    # Write the chat data to a JSON file
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(chat_data, json_file, indent=4)

    print(f"Chat data extracted and saved as {output_path}")

# Check if the correct number of arguments is provided
if len(sys.argv) != 3:
    print("Usage: python script.py input_folder output_folder")
else:
    # Get the input folder and output folder paths from command-line arguments
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    # Iterate through HTML files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.html'):
            # Get the input file path
            print(filename)
            input_file = os.path.join(input_folder, filename)

            # Parse HTML and generate JSON
            parse_html_to_json(input_file, output_folder)
