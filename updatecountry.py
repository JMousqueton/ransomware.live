import openai
import json
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is available
if api_key is None:
    raise ValueError("API key not found in the .env file")

# Open the JSON file for reading
with open('posts.json', 'r') as json_file:
    # Load the JSON data from the file
    data = json.load(json_file)

# Loop through each post and update the "country" field if it's empty
for post in data:
    if not post["country"]:
        # Extract the country code based on post_title
        prompt = f"From which country is based '{post['post_title']}'? Give me only the country code."
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=5,  # Adjust as needed
            api_key=api_key
        )   
        # Extract the country code from the API response
        response_text = response.choices[0].text.strip()
        # Extract the country code from the response text
        #country_code = response_text.split("code is ")[-1].strip('" ')
        country_code = country_code = re.search(r'(?<=code\sis\s)[A-Z]{2}(?="\.)', response_text ).group()

        # If country code is still empty, ask based on the description
        if not country_code:
            prompt = f"Based on this description: '{post['description']}' can you tell me in which country is based the company described ? Give me only the country code."
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=5,  # Adjust as needed
                api_key=api_key
            )
            # Extract the country code from the response
            response_text = response.choices[0].text.strip()
            country_code = country_code = re.search(r'(?<=code\sis\s)[A-Z]{2}(?="\.)', response_text ).group()

        # Update the "country" field with the extracted country code
        if country_code:
            post["country"] = country_code

# Save the updated data back to the JSON file
with open('posts.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

print("Country codes inserted into the 'country' field for posts with empty country.")