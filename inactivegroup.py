import json
from datetime import datetime

# Read the JSON file
with open('posts.json') as file:
    posts_data = json.load(file)

# Define the cutoff date
cutoff_date = datetime(2022, 1, 1)

# Dictionary to store the latest published date for each group name
group_latest_publish_date = {}

# Iterate over each post
for post in posts_data:
    group_name = post['group_name']
    published_date = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
    
    if group_name not in group_latest_publish_date:
        group_latest_publish_date[group_name] = published_date
    elif published_date > group_latest_publish_date[group_name]:
        group_latest_publish_date[group_name] = published_date

# Filter out the group names with any posts published after the cutoff date
filtered_group_names = [group_name for group_name, latest_publish_date in group_latest_publish_date.items() if latest_publish_date <= cutoff_date]

# Sort the filtered group names in alphabetical order
sorted_group_names = sorted(filtered_group_names)

# Print the sorted group names
for group_name in sorted_group_names:
    print(group_name)

