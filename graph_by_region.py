import json
import pandas as pd
import matplotlib.pyplot as plt
import requests
import importlib.util
import sys
import os
from datetime import datetime
from mypycountries import get_country_region
from sharedutils import stdlog, dbglog, errlog  
# For watermark on screenshot 
from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL.PngImagePlugin import PngInfo

# Load the posts.json file from the provided data
with open('posts.json') as f:
    data = json.load(f)

current_year = datetime.now().year

# Extract the year from the discovered date
def get_year(post):
    return post['discovered'][:4]

# Filter posts by year and add region information
def filter_posts_by_year(posts, year):
    posts_year = [post for post in posts if get_year(post) == year]
    for post in posts_year:
        country_code = post['country']
        post['region'] = get_country_region(country_code)
    return posts_year

# Count the number of victims per region
def count_victims_by_region(posts):
    region_counts = {}
    for post in posts:
        region = post['region']
        if region:
            if region in region_counts:
                region_counts[region] += 1
            else:
                region_counts[region] = 1
    return region_counts

def add_watermark(image_path, watermark_image_path='./docs/ransomwarelive.png'):
    """
    Adds a watermark image (with 50% transparency) to the center of the input image and overwrites it.
    
    :param image_path: Path to the image to be watermarked.
    :param watermark_image_path: Path to the watermark image.
    :return: None
    """
    # Open the image to be watermarked
    stdlog('open image ' + image_path)
    original = Image.open(image_path)
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
    
    # Open the watermark image
    #stdlog('open watermark image ' + watermark_image_path)
    watermark = Image.open(watermark_image_path)
    if watermark.mode != 'RGBA':
        watermark = watermark.convert('RGBA')

    # Adjust opacity of watermark
    transparent = Image.new('RGBA', watermark.size, (255, 255, 255, 0))
    for x in range(watermark.width):
        for y in range(watermark.height):
            r, g, b, a = watermark.getpixel((x, y))
            transparent.putpixel((x, y), (r, g, b, int(a * 0.1)))

    watermark = transparent

    # Position watermark in the center
    x = (original.width - watermark.width) // 2
    y = (original.height - watermark.height) // 2

    # Overlay the watermark onto the screenshot
    original.paste(watermark, (x, y), watermark)
    
    # Overwrite the original screenshot
    stdlog('save image ' + image_path)
    original.save(image_path, 'PNG')

# Create pie chart and save as PNG
def create_pie_chart(region_counts, year):
    df = pd.DataFrame(list(region_counts.items()), columns=['Region', 'Victim Count'])
    total_victims = sum(df['Victim Count'])
    percentages = [count / total_victims * 100 for count in df['Victim Count']]
    
    plt.figure(figsize=(10, 7), facecolor='none')  # Make the background transparent
    wedges, texts, autotexts = plt.pie(percentages, labels=df['Region'], autopct='%1.1f%%', startangle=140, textprops={'color': '#42b983'})
    plt.axis('equal')
    plt.title(f'Victim Statistics for {year} per Region\n\n', color='#42b983')  # Change title color
    
    # Customizing the percentage text inside the pie chart to be a darker green
    for autotext in autotexts:
        autotext.set_color('black')  # Dark green

    # Adding footer text
    plt.figtext(0.5, 0.05, 'Source: Ransomware.live © '+ str(current_year), ha='center', fontsize=8, color='#42b983')

    
    output_path = f'./docs/graphs/victim_statistics_{year}_per_region.png'
    plt.savefig(output_path, transparent=True)  # Save the figure with a transparent background
    add_watermark(output_path)
    plt.close()

# Process data for the years 2023 and onward dynamically up to the current year
for year in range(2023, current_year + 1):
    posts_year = filter_posts_by_year(data, str(year))
    region_counts = count_victims_by_region(posts_year)
    create_pie_chart(region_counts, str(year))
