# Pre version to analyse ransom negotiation with chat GPT 
import json
import openai
import argparse
import os
from dotenv import load_dotenv

# Load OpenAI API key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def read_json_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def ask_openai(question, content):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"{content}\n\n{question}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

def extract_details_from_json(json_content):
    # Extract ransom demand
    ransom_demand_question = "How much was the ransom demand, answer only the figure of the amount?"
    ransom_demand = ask_openai(ransom_demand_question, json_content)
    print(f"Ransom Demand: {ransom_demand}")

    # Extract negotiated ransom
    negotiated_ransom_question = "How much was the negotiated ransom, answer only the figure of the amount?"
    negotiated_ransom = ask_openai(negotiated_ransom_question, json_content)
    print(f"Negotiated Ransom: {negotiated_ransom}")

    # Check if victim paid the ransom
    paid_ransom_question = "Did the victim pay the ransom, answer only yes or no?"
    paid_ransom = ask_openai(paid_ransom_question, json_content)
    print(f"Paid Ransom: {paid_ransom}")

def main():
    parser = argparse.ArgumentParser(description='Analyse negotiation json file file using ChatGPT.')
    parser.add_argument('filename', help='Path to the JSON file.')

    args = parser.parse_args()
    json_content = read_json_file(args.filename)
    extract_details_from_json(str(json_content))

if __name__ == "__main__":
    main()
