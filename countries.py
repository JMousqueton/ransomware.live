import json
import pycountry
from sharedutils import stdlog, errlog
from datetime import datetime
import os, hashlib
from countryinfo import CountryInfo
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def format_date(date_string):
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        errlog('Error generating country page')

def count_post_titles_by_country(country_code):
    with open('posts.json', 'r') as file:
        posts_data = json.load(file)    
    count = 0
    for post in posts_data:
        if post.get('country') == country_code:
            count += 1
    return count

def extract_domain(url):
    if '://' not in url:
        url = 'http://' + url  # Assumption to handle URLs without a scheme
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        return parsed_url.netloc.replace('www.','')
    return ''


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
stdlog('Generating countries')



# Read the JSON file
with open('posts.json', 'r') as file:
    data = json.load(file)

# Extract country codes from the 'country' field in each post
country_codes = [post.get('country') for post in data if post.get('country')]

# Get unique country codes
unique_country_codes = set(country_codes)

# Get country names based on country codes, filtering out invalid codes
valid_countries = [pycountry.countries.get(alpha_2=code) for code in unique_country_codes if pycountry.countries.get(alpha_2=code)]


# Sort valid country names alphabetically
sorted_countries = sorted(valid_countries, key=lambda x: x.name)

num_countries = len(sorted_countries)

# Generate image URLs for each country within the country name
image_urls = [f"![{country.alpha_2.upper()}](https://images.ransomware.live/flags/{country.alpha_2.upper()}.svg ':size=32x24 :no-zoom') {country.name}" for country in sorted_countries]

table_rows = []
for country in sorted_countries:
    country_name = country.name
    country_code = country.alpha_2.lower()
    country_link = f"[{country_name}](/country/{country_code})"
    country_count = count_post_titles_by_country(country.alpha_2.upper())
    flag_image = f"![{country.alpha_2.upper()}](https://images.ransomware.live/flags/{country.alpha_2.upper()}.svg ':size=32x24 :no-zoom')"
    table_rows.append(f"{flag_image} {country_link} ({country_count}) ")

# Calculate the number of rows needed in the table
num_cols = 4
num_rows = (len(image_urls) + num_cols - 1) // num_cols  # Round up division to determine the number of rows

# Format the combined country names and image URLs into a Markdown table with 5 columns
markdown_table = "# 🌍 Ransomware's victims by country\n\n"

markdown_table += "> [!INFO]\n"
markdown_table += "> The country identification on Ransomware.live might not always be accurate as it uses artificial intelligence to deduce the location of victims.\n"
markdown_table += "> If you want to notify me about any mistake, you can either [open an issue](https://github.com/JMousqueton/ransomware.live/issues) on the github repository of Ransomware.live or [contact me](https://static.ransomware.live/contact.html).\n\n"


markdown_table += "|   |   |   |   | \n"
markdown_table += "|---|---|---|---|\n"
#
for i in range(num_rows):
    start = i * num_cols
    end = min(start + num_cols, len(table_rows))
    row_data = table_rows[start:end]
    row = "| " + " | ".join(row_data) + " " * (11 * num_cols - len(row_data) * 11 - 1) + "|\n"  # Adjust for varying data size
    markdown_table += row

markdown_table +="\n\n"
markdown_table += str(len(sorted_countries))
markdown_table += " attacked countries detected"

# Save the Markdown table in the ./docs/ directory
output_file_path = './docs/country.md'

with open(output_file_path, 'w') as table_file:
    table_file.write(markdown_table)

# Load the JSON data from the file
with open('eucert.json') as json_file:
    cert = json.load(json_file)

def get_cert_info_by_country(country_code):
    cert_info = []
    for entry in cert['data']:
        if entry['country-code'] == country_code:
            cert_info.append({
                'team_name': entry['team-name'],
                'website': entry['website'],
                'email': entry['email']
            })
    return cert_info

def get_teams_info_by_country(country_code, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    certs_info = []

    # Find all rows in the table body
    rows = soup.find('table', {'class': 'data-preview'}).find('tbody').find_all('tr')

    # Extracting information from each row based on the provided country code
    for row in rows:
        country = row.find('span', {'class': 'flag'}).text
        country = country.lstrip()
        if country.lower() == country_code.lower():
            link = row.find('a').get('href')
            name = row.find('a').text
            row_id = row.get('id')
            certs_info.append({
                'country': country,
                'link': link,
                'name': name,
                'row_id': row_id
            })
    return certs_info

## Create page per country 
def create_country_victims_file(country_code, victims_data,html_content):
    country = pycountry.countries.get(alpha_2=country_code.upper())
    NowTime=datetime.now()
    if country:
        country_name = country.name
        file_path = f"./docs/country/{country_code.lower()}.md"
        with open(file_path, 'w') as country_file:
            country_file.write(f"# Ransomware's victims in {country_name} ![{country_code.upper()}](https://images.ransomware.live/flags/{country_code.upper()}.svg)\n\n")
            try:
                country = CountryInfo(country_code)
                try: 
                    capital = country.capital()
                except:
                    capital = 'N/A' 
                try:
                    population = str("{:,}".format(country.population())) + " people" 
                except: 
                    population = 'N/A'
                try:
                    area = str("{:,}".format(country.area())) + " square kilometers" 
                except: 
                    area = "N/A"
                try:
                    timezones = ', '.join(country.timezones()) 
                except:
                    timezones = 'N/A'   
            except:
                stdlog('Error getting info for country ' + country_name + ' (' + country_code + ')')    

            ### GET European cert
            if country_code.lower() == 'uk':
                country_code == 'GB'
            certs_for_country = get_cert_info_by_country(country_code.lower())
            if certs_for_country:
                certlist = '| CSIRT name | Website | Email |\n'
                certlist += '|---|---|---|\n'
                for cert in certs_for_country:
                    #certlist += '|' +  cert['team_name'] + '|' + cert['website'] + '|' + cert['email'].replace('@','🌀')+'\n'
                    certlist += '| ' +  cert['team_name'] + ' | ' + cert['website'] + ' | ' + cert['email']+' | \n'
            else:
                certs = get_teams_info_by_country(country_code, html_content)
                if certs:
                    certlist = '| CSIRT name | Link |\n'
                    certlist += '|---|---|\n'

                    # Displaying the extracted information
                    for cert in certs:
                        certlist += '| ' +  cert['name'] + ' | https://www.first.org'+cert['link']+ ' |\n' 
                else:
                    stdlog(f"No CERTs found for country code {country_code.upper()}.")
                    certlist= 'No CERT/CSIRT found'

            country_file.write('### Country Information \n')
            country_file.write('<!-- tabs:start -->\n')
            country_file.write('#### **Capital**\n')
            country_file.write(capital+"\n")
            country_file.write('#### **Population**\n') 
            country_file.write(population+"\n")
            country_file.write('#### **Area**\n')
            country_file.write(area+"\n")
            country_file.write('#### **Time Zones**\n') 
            country_file.write(timezones+"\n")
            country_file.write('#### **CSIRT**\n') 
            country_file.write(certlist+"\n")
            country_file.write('<!-- tabs:end -->\n') 


            country_file.write('\n \n')

            country_file.write(f"> [!INFO]\n")
            country_file.write(f"> The country identification on Ransomware.live might not always be accurate as it uses artificial intelligence to deduce the location of victims.\n")
            country_file.write(f"> If you want to notify me about any mistake, you can either [open an issue](https://github.com/JMousqueton/ransomware.live/issues) on the github repository of Ransomware.live or [contact me](https://static.ransomware.live/contact.html).\n\n")

            counter = 0 
            country_file.write(f"\n| Discovered date | Attack date | Victim | Ransomware Group | 📸 | 🕵🏻‍♂️ | \n")
            country_file.write(f"|---|---|---|---|---|---|\n")
            for victim in victims_data:
                if victim['discovered_date'] == victim['published_date']:
                    victim['published_date'] = ' '
                # screenpost='❌'
                screenpost=' '
                if victim['post_url'] is not None: 
                     # Create an MD5 hash object
                    hash_object = hashlib.md5()
                    # Update the hash object with the string
                    hash_object.update(victim['post_url'].encode('utf-8'))
                    # Get the hexadecimal representation of the hash
                    hex_digest = hash_object.hexdigest()
                    if os.path.exists('docs/screenshots/posts/'+hex_digest+'.png'):
                        screenpost='<a href="https://images.ransomware.live/screenshots/posts/' + hex_digest + '.png" target=_blank>👀</a>'


                    hash_object = hashlib.md5()
                    # Update the hash object with the string
                    hash_object.update(victim['name'].lower().encode('utf-8'))
                    # Get the hexadecimal representation of the hash
                    hex_digest = hash_object.hexdigest()
                    if os.path.exists('docs/domain/'+hex_digest+'.md'):
                        infostealer=' [🔎](domain/'+hex_digest+') '
                    elif victim['website']:
                        domain = extract_domain(victim['website'].lower()) #.replace('http://','').replace('https://','').replace('www.','')
                        hash_object = hashlib.md5()
                        hash_object.update(domain.encode('utf-8'))
                        hex_digest = hash_object.hexdigest()
                        if  os.path.exists('docs/domain/'+hex_digest+'.md'):
                            infostealer=' [🔎](domain/'+hex_digest+') '
                        else:
                            infostealer = ''
                    else:
                        infostealer = ''
                country_file.write(f"|{victim['discovered_date']}|{victim['published_date']}|[{victim['name'].replace('|','-')}](https://google.com/search?q={victim['name'].replace('|','-').replace(' ','+')})|[{victim['group_name']}](group/{victim['group_name']})| {screenpost}| {infostealer} |\n")
                counter += 1 
            country_file.write(f"\n\n{counter} victims found\n\n")
            country_file.write('Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')



# Load posts from JSON file
with open('posts.json', 'r') as file:
    posts_data = json.load(file)

# Group victims by country code
victims_by_country = {}
for post in posts_data:
    country_code = post.get('country')
    victim_name = post.get('post_title')
    published_date = format_date(post.get('published'))
    post_url = post.get('post_url', '')
    group_name = post.get('group_name')
    website = post.get('website')
    discovered_date = format_date(post.get('discovered'))

    if country_code and victim_name and published_date and discovered_date and group_name:
        if country_code not in victims_by_country:
            victims_by_country[country_code] = []
        victims_by_country[country_code].append({
            'name': victim_name,
            'published_date': published_date,
            'discovered_date': discovered_date,
            'post_url': post_url, 
            'group_name': group_name,
            'website': website
        })


# Fetch HTML content from the URL
url = 'https://www.first.org/members/teams/'
response = requests.get(url)
html_content = response.content

# Sort victims by published_date in descending order
for country_code, victims_data in victims_by_country.items():
    victims_by_country[country_code] = sorted(victims_data, key=lambda x: datetime.strptime(x['discovered_date'], '%Y-%m-%d'), reverse=True)

# Create individual country files for victims
for country_code, victims_data in victims_by_country.items():
    stdlog('Create page for ' + country_code)
    create_country_victims_file(country_code, victims_data,html_content)

