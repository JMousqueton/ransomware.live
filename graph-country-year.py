import json
import matplotlib.pyplot as plt
from collections import defaultdict
import pycountry
from datetime import datetime
from sharedutils import stdlog, dbglog, errlog  
# For watermark on screenshot 
from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL.PngImagePlugin import PngInfo


Path='./docs/graphs/'

def get_country_name(code):
    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name if country else 'Unknown'
    except AttributeError:
        return 'Unknown'


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
    stdlog('open watermark image ' + watermark_image_path)
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


def graphTop10Countries(year=''):
    # Load the JSON data from the file
    with open('posts.json') as file:
        posts_data = json.load(file)

    if year:
        # Filter entries with a defined and non-empty 'country' field and discovered date in year
        filtered_data = [
        post for post in posts_data
        if 'country' in post
        and post['country']
        and post.get('discovered', '').startswith(str(year))
        ]
        filename = Path+'top10countries-'+str(year)+'.png'
    else:
        # Filter entries with a defined and non-empty 'country' field
        filtered_data = [post for post in posts_data if 'country' in post and post['country']]
        filename = Path+'top10countries.png'

    # Extract country codes from the filtered data
    country_codes = [post['country'] for post in filtered_data]

    # Extract discovered dates for each entry with a valid country in 2023
    discovered_dates = [post['discovered'] for post in filtered_data]

    # Find the earliest discovered date in 2023
    earliest_date = min(discovered_dates, default=None)

    # Convert earliest discovered date to a more readable format
    if earliest_date:
        earliest_date = datetime.strptime(earliest_date, '%Y-%m-%d %H:%M:%S.%f').strftime('%d/%m/%Y')

    # Count occurrences of country codes
    country_statistics = defaultdict(int)
    for code in country_codes:
        country_statistics[code] += 1

    # Sort countries based on the number of victims
    sorted_countries = dict(sorted(country_statistics.items(), key=lambda x: x[1], reverse=True))

    # Consider top 10 countries
    top_10_countries = dict(list(sorted_countries.items())[:10])

    # Extract data for the pie chart and collect country names
    labels = list(top_10_countries.keys())
    sizes = list(top_10_countries.values())

    country_names = {code: get_country_name(code) for code in labels}

    #country_names = {code: pycountry.countries.get(alpha_2=code).name for code in labels}

    # Plotting the pie chart for top 10 countries
    plt.figure(figsize=(10, 8))
    patches, texts, autotexts = plt.pie(
        sizes, labels=labels, autopct='%1.1f%%', startangle=140,
        textprops=dict(color="w")  # Change label text color to white
    )
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Title with the number of entries with a valid country and earliest discovered date in 2023
    total_victims = sum(country_statistics.values())
    if year:
        plt.title(f"Top 10 countries in {year} based on {total_victims} victims")
    else:
        plt.title(f"Top 10 countries based on {total_victims} victims with country since {earliest_date}")

    # Add country codes (2 letters) under each percentage in the pie chart
    for autotext, label in zip(autotexts, labels):
        autotext.set_text(f"{autotext.get_text()} ({label})")

    # Create a legend with rank, country code, country name, and the previous legend
    legend_labels = [
        f"#{i+1} - {label} - {country_names.get(label, 'Unknown')} ({top_10_countries[label]})"
        for i, label in enumerate(labels)
    ]
    plt.legend(patches, legend_labels, loc="best", fontsize='small')

    # Save the plot as an image named 'top10_defined_countries_2023.png'
    plt.savefig(filename)
    add_watermark(filename)

    # Show the plot
    #plt.show()

if __name__ == "__main__":
    print(
    '''
       _______________                        |*\_/*|________
      |  ___________  |                      ||_/-\_|______  |
      | |           | |                      | |           | |
      | |   0   0   | |                      | |   0   0   | |
      | |     -     | |                      | |     -     | |
      | |   \___/   | |                      | |   \___/   | |
      | |___     ___| |                      | |___________| |
      |_____|\_/|_____|                      |_______________|
        _|__|/ \|_|_.............💔.............._|________|_
       / ********** \                          / ********** \ 
     /  ************  \   ransomware.live     /  ************  \ 
    --------------------                    --------------------
    '''
    )
    stdlog('Generating graph')
    graphTop10Countries()
    graphTop10Countries(2023)
    graphTop10Countries(2024)