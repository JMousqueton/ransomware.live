import json
import hashlib
import os.path

# Open the JSON file
with open('posts.json', 'r') as file:
    # Load the JSON data
    data = json.load(file)

# Loop through each post in the data
for post in data:
    # Check if the "post_url" value is not empty
    if post.get("post_url"):
        # Calculate the MD5 checksum of the "post_url" value
        post_url_bytes = post["post_url"].encode('utf-8')
        post_md5 = hashlib.md5(post_url_bytes).hexdigest()
        # Check if a screenshot file exists for the post
        screenshot_file = f"./docs/screenshots/posts/{post_md5}.png"
        if not os.path.exists(screenshot_file):
            # If a screenshot file does not exist, print the "post_url" value
            print("python3 postscreenshot.py " + post["post_url"])

