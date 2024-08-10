import json

# Function to map sender ID to party name
def map_sender_to_party(sender_id):
    return "dragonforce" if sender_id == 1 else "victim"

# Function to transform the data from the raw format to the desired format
def transform_data(raw_data):
    # Extract the relevant chat
    chat = raw_data["data"]["post"]["chats"][0]

    # Initialize the new structure
    transformed_data = {
        "chats_id": chat.get("uuid", ""),
        "contents": []
    }

    # Iterate over each message in the raw data and transform it
    for message in chat.get("messages", []):
        transformed_message = {
            "timestamp": message.get("created_at", ""),
            "content": message.get("message", ""),
            "party": map_sender_to_party(message.get("sender"))
        }
        # Handle attachments if they exist
        if "attachment" in message:
            transformed_message["content"] = f"{message['attachment']['filename']} filesize:{message['attachment']['filesize']}"
        
        transformed_data["contents"].append(transformed_message)
    
    return transformed_data

# Read the raw JSON file
with open('./raw.json', 'r') as raw_file:
    raw_data = json.load(raw_file)

# Transform the data
transformed_data = transform_data(raw_data)

# Write the transformed data to a new JSON file
output_file_path = './resultat.json'
with open(output_file_path, 'w') as output_file:
    json.dump(transformed_data, output_file, indent=4)

print(f"Transformation complete. Data written to {output_file_path}")
