import json

# Load the JSON data from the file
with open('posts.json', 'r') as file:
    data = json.load(file)

# Iterate through each entry and add the "country" field
for entry in data:
    entry["country"] = ""

# Write the updated data back to the file
with open('posts.json', 'w') as file:
    json.dump(data, file, indent=4)

