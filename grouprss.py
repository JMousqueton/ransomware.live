import json
from feedgen.feed import FeedGenerator
import os
import hashlib
import html
from datetime import datetime, timezone

# Read the posts.json file
with open('posts.json', 'r') as file:
    posts = json.load(file)

# Group posts by group_name
grouped_posts = {}
for post in posts:
    group_name = post['group_name']
    if group_name not in grouped_posts:
        grouped_posts[group_name] = []
    grouped_posts[group_name].append(post)

# Get the size of the default image
default_image_path = './docs/ransomware.png'
default_image_size = str(os.path.getsize(default_image_path))

# Create RSS feeds for each group_name
for group_name, group_posts in grouped_posts.items():
    fg = FeedGenerator()
    fg.title(f"{group_name} RSS Feed")
    fg.link(href=f"https://www.ransomware.live/grouprss/{group_name}.xml", rel='self')
    fg.description(f"RSS feed for {group_name} posts")
    fg.generator('Ransomware.live by Julien Mousqueton')

    for post in group_posts:
        fe = fg.add_entry()
        fe.title(post['post_title'])
        # Escape HTML characters in description
        escaped_description = html.escape(post.get('description', 'No description available'))
        fe.description(escaped_description)

        # Check if post_url is not empty and corresponding image file exists
        post_url = post.get('post_url')
        if post_url:
            url_md5 = hashlib.md5(post_url.encode()).hexdigest()
            image_path = f"docs/screenshots/posts/{url_md5}.png"
            if os.path.exists(image_path):
                image_link = f"https://images.ransomware.live/screenshots/posts/{url_md5}.png"
                # Get the real size of the image
                image_size = str(os.path.getsize(image_path))
                fe.enclosure(image_link, image_size, 'image/png')  # Set image as an enclosure in the feed
            else:
                # Assign default image if no image is set
                fe.enclosure('https://www.ransomware.live/ransomware.png', default_image_size, 'image/png')  # Set default image as an enclosure
        else:
            # Assign default image if no post_url is available
            fe.enclosure('https://www.ransomware.live/ransomware.png', default_image_size, 'image/png')  # Set default image as an enclosure
        
        # Add published date (using 'published' field)
        published_date = post.get('published')
        if published_date:
            # Convert published_date to a datetime object with timezone info
            dt = datetime.strptime(published_date, '%Y-%m-%d %H:%M:%S.%f')
            dt_with_tz = dt.replace(tzinfo=timezone.utc)
            fe.pubDate(dt_with_tz)
        
        # Add link for each item
        item_link = f"https://www.ransomware.live/#/group/{group_name}"
        fe.link(href=item_link)

        # Generate MD5 hash for the title
        title_md5 = hashlib.md5(post['post_title'].encode()).hexdigest()
        guid_link = f"https://www.ransomware.live/?={title_md5}"
        fe.guid(guid_link)

    # Save the RSS feed to a file in the 'docs/grouprss' directory
    output_dir = 'docs/grouprss'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{group_name}.xml")
    fg.rss_file(output_file)

# Generate an XML file with references to all the RSS feeds
xml_content = '<?xml version="1.0" encoding="UTF-8" ?>\n<feeds>\n'
for group_name in grouped_posts.keys():
    xml_content += f'\t<feed>\n\t\t<name>{group_name}</name>\n\t\t<url>https://www.ransomware.live/grouprss/{group_name}.xml</url>\n\t</feed>\n'

xml_content += '</feeds>\n'

# Save the XML content to a file
xml_file_path = 'docs/grouprss/index.xml'
os.makedirs(os.path.dirname(xml_file_path), exist_ok=True)
with open(xml_file_path, 'w') as xml_file:
    xml_file.write(xml_content)
