import json
import requests

# Load the JSON file from the URL
assessments_url = 'https://raw.githubusercontent.com/Casualtek/Cyberwatch/main/assessments.json'
response = requests.get(assessments_url)
assessments_data = response.json()

# Load the local posts.json file
with open('./data/victims.json', 'r') as posts_file:
    posts_data = json.load(posts_file)

# Create a dictionary from assessments for quick lookup
assessments_dict = {(item['domain'], item['group']): item['country'] for item in assessments_data}

# Update the country field in posts_data only if both domain and group match
for post in posts_data:
    if not post.get('country'):  # Proceed only if country is empty
        domain = post.get('website')
        victim = post.get('post_title')
        group = post.get('group_name')

        if (domain, group) in assessments_dict:
            post['country'] = assessments_dict[(domain, group)]
            print(f"*  {domain} --> {assessments_dict[(domain, group)]}")
        elif (victim, group) in assessments_dict:
            post['country'] = assessments_dict[(victim, group)]
            print(f"** {victim} --> {assessments_dict[(victim, group)]}")

# Save the updated posts_data back to the same posts.json file
with open('./data/victims.json', 'w') as posts_file:
    json.dump(posts_data, posts_file, indent=4)

