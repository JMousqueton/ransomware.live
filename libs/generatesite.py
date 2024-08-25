# -*- coding: utf-8 -*-
import os, hashlib, json,re 
from datetime import datetime, timedelta, date
from dotenv import load_dotenv 
import logging
import fnmatch
from collections import Counter, defaultdict
import urllib.parse
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
#import datetime
import pandas as pd
from ransomwarelive import stdlog, errlog, openjson, clean_markdown, get_tools_by_group
from countryinfo import CountryInfo
import requests
from bs4 import BeautifulSoup
import pycountry


env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)

POST_SCREENSHOT_DIR = os.getenv('POST_SCREENSHOT_DIR')
SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR')
DATA_DIR = os.getenv('DATA_DIR')
REMOVEREQUESTS = DATA_DIR + 'removerequests.json'
GROUPS_FILE = os.getenv('GROUPS_FILE')
VICTIMS_FILE = os.getenv('VICTIMS_FILE')

## Tuning 
GROUPS_FILE = DATA_DIR + GROUPS_FILE
VICTIMS_FILE = DATA_DIR + VICTIMS_FILE


# Make more variable ;) 

def get_removal(victim, group, json_file=REMOVEREQUESTS):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    if victim == data.get("victim_name") and group == data.get("group_name"):
        applicant = data.get("applicant")
        return applicant
    return None

def find_matching_victims(victim_hidden, group):
    matching_pairs = ''
    if '*' not in victim_hidden:
        return matching_pairs
    matching_pairs = "Not Found"
    try:
        with open(VICTIMS_FILE, 'r') as json_file:
            data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        stdlog(f"Error reading VICTIMS_FILE: {e}")
        return matching_pairs
    # Filter victims by group and exclude those with asterisks in their names
    victims = [entry['post_title'] for entry in data if entry['group_name'] == group and '*' not in entry['post_title']]
    # Convert the victim_hidden pattern into a regex pattern
    regex_pattern = re.escape(victim_hidden).replace(r'\*', r'.').replace(r'\.', r'[-.\w]*').lower()
    # Iterate through potential victims
    for victim in victims:
        if re.fullmatch(regex_pattern, victim.lower()):
            stdlog(f"Victim: {victim_hidden} could be: {victim}")
            return victim  # Return the first match found
    return matching_pairs



def directory_exists(directory):
    if os.path.exists(directory) and os.path.isdir(directory):
        return True
    else:
        return False

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(fmt, t):
    return t.strftime(fmt).replace('{S}', str(t.day) + suffix(t.day))

def hostcount():
    groups = openjson(GROUPS_FILE)
    host_count = 0
    for group in groups:
        for host in group['locations']:
            host_count += 1
    return host_count

def groupcount():
    groups = openjson(GROUPS_FILE)
    return len(groups)

def onlinecount():
    groups = openjson(GROUPS_FILE)
    online_count = 0
    for group in groups:
        for host in group['locations']:
            if host['available'] is True:
                online_count += 1
    return online_count

def postslast24h():
    '''returns the number of posts within the last 24 hours'''
    post_count = 0
    posts = openjson(VICTIMS_FILE)
    for post in posts:
        datetime_object = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime_object > datetime.now() - timedelta(hours=24):
            post_count += 1
    return post_count

def postssince(days):
    '''returns the number of posts within the last x days'''
    post_count = 0
    posts = openjson(VICTIMS_FILE)
    for post in posts:
        datetime_object = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime_object > datetime.now() - timedelta(days=days):
            post_count += 1
    return post_count

def postsyear(annee):
    '''
    returns the number of posts last year
    '''
    post_count = 0
    posts = openjson(VICTIMS_FILE)
    for post in posts:
        datetime_object = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime_object.year == annee:
            post_count += 1
    return post_count

def parsercount():
    directory = './parsers/'
    pattern = '*.py'
    exclude_pattern = '__init__.py'
    py_files = [file for file in os.listdir(directory) if fnmatch.fnmatch(file, pattern)]
    py_files = [file for file in py_files if file != exclude_pattern]
    return len(py_files)

def postcount():
    post_count = 1
    posts = openjson(VICTIMS_FILE)
    for post in posts:
        post_count += 1
    return post_count


def count_OpenCTI(log_file_path, user_agent="OpenCTI Connector"):
    # Regular expression to extract the IP address and user agent from the log file
    log_pattern = re.compile(r'(?P<ip>\b(?:\d{1,3}\.){3}\d{1,3}\b).*?"[^"]*".*?"([^"]*)".*?"(?P<user_agent>[^"]+)"')
    unique_ips = set()
    try: 
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                match = log_pattern.search(line)
                if match:
                    ip = match.group('ip')
                    ua = match.group('user_agent')
                    if user_agent in ua:
                        unique_ips.add(ip)

        return len(unique_ips)
    except:
        return('0')


def recentdiscoveredposts(top):
    '''
    create a list the last X posts (most recent)
    '''
    stdlog('Finding recent posts')
    posts = openjson(VICTIMS_FILE)
    # sort the posts by timestamp - descending
    sorted_posts = sorted(posts, key=lambda x: x['discovered'], reverse=True)
    # create a list of the last X posts
    recentposts = []
    for post in sorted_posts:
        recentposts.append(post)
        if len(recentposts) == top:
            break
    stdlog('recent posts generated')
    return recentposts

def recentattackedposts(top):
    '''
    create a list the last X posts (most recent)
    '''
    stdlog('Finding recent posts')
    posts = openjson(VICTIMS_FILE)
    # sort the posts by timestamp - descending
    #sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
    sorted_posts = sorted(posts, key=lambda x: x['published'] if x.get('published') else x['discovered'], reverse=True)
    # create a list of the last X posts
    recentposts = []
    for post in sorted_posts:
        recentposts.append(post)
        if len(recentposts) == top:
            break
    stdlog('recent posts generated')
    return recentposts


def extract_domain(url):
    if '://' not in url:
        url = 'http://' + url  # Assumption to handle URLs without a scheme
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        return parsed_url.netloc.replace('www.','')
    return ''

def grouppostavailable(groupname):
    grouppost_count = 0
    posts = openjson(VICTIMS_FILE)
    for post in posts:
        if post['group_name'] == groupname:
            grouppost_count += 1
    if grouppost_count > 0:
        return True
    else:
        return False

def postcountgroup(groupname):
    grouppost_count = 0
    posts = openjson(VICTIMS_FILE)
    for post in posts:
        if post['group_name'] == groupname:
            grouppost_count += 1
    return grouppost_count

def grouppostcount(groupname):
    grouppost_count = 0
    posts = openjson(VICTIMS_FILE)
    for post in posts:
        if post['group_name'] == groupname:
            grouppost_count += 1
    if grouppost_count > 1:
        grouppost_count = str(grouppost_count) + ' victims found'
    elif grouppost_count == 1:
        grouppost_count = '1 victim found'
    elif grouppost_count ==0:
        grouppost_count = 'no victim found'
    return grouppost_count

def redactedlink(text):
    try:
        pattern = r"(https://mega\.nz/folder/)[^#]+"
        redacted_text = re.sub(pattern, r"\1[REDACTED]", text)

        pattern = r"(https://anonfiles\.com/)[^/]+"
        redacted_text = re.sub(pattern, r"\1[REDACTED]", redacted_text)

        pattern = r"(https://dropmefiles\.com/)[^ ]+"
        redacted_text = re.sub(pattern, r"\1[REDACTED]", redacted_text)
        
        pattern = r"(https://www\.sendbig\.com/view-files/\?Id=)[^&]+"
        redacted_text = re.sub(pattern, r"\1[REDACTED]", redacted_text)

        pattern = r"(https://www\.sendspace\.com/file/)\S+"
        redacted_text = re.sub(pattern, r"\1[REDACTED]", redacted_text)

        pattern = r"(https://gofile\.io/d/)\S+"
        redacted_text = re.sub(pattern, r"\1[REDACTED]", redacted_text)

        # Regular expression pattern to match valid email addresses
        email_pattern = r'(?<!\S)[\w\.-]+@[\w\.-]+\.\w+(?!\S)'
        # Function to replace '@' with '_AT_'
        def replace_at(match):
            return match.group().replace('@', '_AT_')
        # Replace all occurrences of the pattern with the modified email
        redacted_text = re.sub(email_pattern, replace_at, redacted_text)
    
        return redacted_text
    
    except:
        return text

def monthlypostcount():
    '''
    returns the number of posts within the current month
    '''
    post_count = 0
    posts = openjson(VICTIMS_FILE)
    current_month = datetime.now().month
    current_year = datetime.now().year
    for post in posts:
        datetime_object = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime_object.year == current_year and datetime_object.month == current_month:
            post_count += 1
    return post_count

def currentmonthstr():
    '''
    return the current, full month name in lowercase
    '''
    return datetime.now().strftime('%B').lower()

def month_name(month_number):
  months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
  return months[month_number - 1]

def month_digit(month_number):
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    return months[month_number - 1]

def write_domain_info(domain, employees, users, third_parties, employees_url, users_url, update):
    # Generate MD5 hash of the domain
    md5_hash = hashlib.md5(domain.encode()).hexdigest()
    file_path = f"./docs/domain/{md5_hash}.md"

    # Ensure the directories exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if float(employees) > 0:
        employees = '`'+str(employees)+'`'
    if float(users) > 0:
        users = '`'+str(users)+'`'
    if float(third_parties) > 0:
        third_parties = '`'+str(third_parties)+'`'
    if float(employees_url) > 0:
        employees_url = '`'+str(employees_url)+'`'
    if float(users_url) > 0:
        users_url = '`'+str(users_url)+'`'

    # Markdown content
    markdown_content = f"""## Information for domain: **{domain}**

![logo {domain}](https://logo.clearbit.com/{domain} ":no-zoom")

> [!INFO] `Information stealer` (infostealer) is a malware—malicious software designed to steal victim information, including passwords

The corporate infrastructure for `{domain}` could have been compromised by Infostealer.

#### Compromised Credentials<sup>1</sup>

| Compromised Employees | Compromised Users | 
| ---- | ---- |
| {employees} | {users} |

#### External surface attack<sup>2</sup> 

| Employee URLs | Users URLs | 
| ---- | ---- |
| {employees_url} | {users_url} | 


> This information is provided by [HudsonRock](https://hudsonrock.com/search?domain={domain})

> [!TIP]
> (1) **Compromised credentials** of employees, partners and customers.
>
> (2) **External surface attack** : Discovered IT services that hackers could use to infiltrate the company and put it at risk.
 

* Data information : {update}
"""

    # Write to Markdown file
    with open(file_path, 'w') as md_file:
        md_file.write(markdown_content)




#### 
friendly_tz = custom_strftime('%B {S}, %Y', datetime.now()).lower().capitalize()
NowTime=datetime.now()


def writeline(file, line, file2=None):
    '''write line to file'''
    with open(file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
        f.close()
    if file2:
        with open(file2, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
            f.close()




def clean_string(s):
    s = s.replace('|', '').replace('\t', '').replace('\b', '').replace('\n', '').strip()
    s = re.sub(' +', ' ', s)  # Replace multiple spaces with a single space
    return s

def capitalize_first_letter(s):
    return s[:1].upper() + s[1:]

def list_files_in_directory(directory):
    file_list = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    
    return file_list

def generate_sitemapXML(base_url, pages, note_directories, output_file="./docs/sitemap.xml"):
    # Create the root element
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Add the static URLs
    static_urls = [
        "recentvictims",
        "recentcyberattacks",
        "allcyberattacks",
        "cartography",
        "recentdiscoveredvictims",
        "lastvictimspergroup",
        "ransomnotes",
        "negotiations",
        "stats",
        "stats?id=victims-by-month",
        "stats?id=victims-by-month-cumulative",
        "stats?id=_2023",
        "stats?id=_2022",
        "about",
        "CHANGELOG"
    ]

    for page in static_urls:
        # Create a URL entry for each static page
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{base_url}/#{page}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = date.today().isoformat()

    for page in pages:
        # Create a URL entry for each page
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{base_url}/#/group/{page['name']}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = date.today().isoformat()
    
    # Add URLs based on note directories
    note_directories = sorted(note_directories)
    for directory in note_directories:
        directory = directory[:-3]
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{base_url}/#/notes/{directory}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = date.today().isoformat()

    directory_path = "./docs/negotiation/"
    for file in list_files_in_directory(directory_path):
        page = file.replace('./docs','')
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{base_url}/#{page}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = date.today().isoformat()

    directory_path = "./docs/country/"
    for file in list_files_in_directory(directory_path):
        page = file.replace('./docs','')
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{base_url}/#{page}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = date.today().isoformat()
    
    directory_path = "./docs/domain/"
    for file in list_files_in_directory(directory_path):
        page = file.replace('./docs','').replace('.md','')
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{base_url}/#{page}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = date.today().isoformat()


    # Create an ElementTree object and write it to a file
    tree = ET.ElementTree(urlset)
    tree.write(output_file, encoding="UTF-8", xml_declaration=True)

def json2cvs():
    df = pd.read_json (r'./data/victims.json')
    df.to_csv (r'docs/victims.csv', index = None) 


def generate_sitemapHTML(base_url, pages, note_directories, output_file="./docs/sitemap.xml"):
    with open(output_file, "w") as file:
        file.write("<!DOCTYPE html>\n")
        file.write("<html>\n")
        file.write("<head>\n")
        file.write("<title>Ransomware.live Sitemap</title>\n")
        file.write("</head>\n")
        file.write("<body>\n")
        file.write("<h1>Sitemap</h1>\n")

        # Generate links to static pages
        static_urls = [
            ("Recent Victims", "recentvictims"),
            ("Recent Cyberattacks", "recentcyberattacks"),
            ("Ransom Notes", "ransomnotes"),
            ("Negotiations", "negotiations"),
            ("Stats", "stats"),
            ("Stats Victims by month", "stats?id=victims-by-month"),
            ("Stats Victims by month cumulative", "stats?id=victims-by-month-cumulative"),
            ("Stats for 2023", "stats?id=_2023"),
            ("Stats for 2022", "stats?id=_2022"),
            ("Stats for 2024", "stats?id=_2024"),
            ("Ransomware attacks by country", "country"),
            ("Ransomware discovered victims", "recentdiscoveredvictims"),
            ("About Ransomware.live", "about"),
            ("Changelog", "CHANGELOG")
        ]

        file.write("<ul>\n")
        for title, url in static_urls:
            file.write(f'<li><a href="{base_url}/#{url}">{title}</a></li>\n')
        file.write("</ul>\n")

        # Generate links to pages from groups.json
        file.write("<ul>\n")
        for page in pages:
            file.write(f'<li><a href="{base_url}/#/group/{page["name"]}">Profile for {capitalize_first_letter(page["name"])}</a></li>\n')
        file.write("</ul>\n")

        # Generate links to note directories
        file.write("<ul>\n")
        note_directories = sorted(note_directories)
        for directory in note_directories:
            directory = directory[:-3]
            file.write(f'<li><a href="{base_url}/#/notes/{directory}">Ransom Note for {capitalize_first_letter(directory)}</a></li>\n')
        file.write("</ul>\n")


        file.write("</body>\n")
        file.write("</html>\n")




#### MAIN FUNCTION 

def mainpage():
    stdlog('generating main page')
    uptime_sheet = 'docs/README.md'
    dir_path = r'docs/screenshots'
    screenshots=(len([entry for entry in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, entry))]))
    dir_path = r'docs/ransomware_notes'
    nbransom_notes = 0
    for root, dirs, files in os.walk(dir_path):
        # On ignore le répertoire .git
        if ".git" in dirs:
            dirs.remove(".git")
        # Pour chaque fichier trouvé, on incrémente le compteur
        nbransom_notes += len(files)
    dir_path = r'docs/screenshots/posts'
    nbscreenshots = 0
    for root, dirs, files in os.walk(dir_path):
        # Pour chaque fichier trouvé, on incrémente le compteur
        nbscreenshots += len(files)

    dir_path = r'docs/negotiation'    
    # nbransom_notes=sum([len(folder) for r, d, folder in os.walk(dir_path)])-4
    nbsnego = 0
    for root, dirs, files in os.walk(dir_path):
        # Pour chaque fichier trouvé, on incrémente le compteur
        nbsnego += len(files)

    dir_path = r'docs/domain'    
    nbsinfostealer = 0
    for root, dirs, files in os.walk(dir_path):
        # Pour chaque fichier trouvé, on incrémente le compteur
        nbsinfostealer += len(files)

    with open(uptime_sheet, 'w', encoding='utf-8') as f:
        f.close()
    writeline(uptime_sheet, '_' + friendly_tz + '_')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet, '_Tracking ransomware\'s victims since April 2022_')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet,'> A **ransomware** is a type of malware used by cybercriminals to encrypt the victim\'s files and make them inaccessible unless they pay the ransom. Today cybercriminals are more sophisticated, and they not only encrypt the victim\'s files also they leaking their data to the Darknet unless they will pay the ransom.')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet, '>[!NOTE]')
    writeline(uptime_sheet, '>_`Ransomware.live` monitors the extortion sites used by ransomware groups. The information posted on this website is dynamically updated in near real-time._')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet, '>[!TIP]')
    writeline(uptime_sheet, '> You can query _`ransomware.live`_ intel by requesting the **FREE** [`API`](https://api.ransomware.live), the [`RSS Feed`](https://ransomware.live/rss.xml) or [`downloading`](https://data.ransomware.live/victims.json) the database.')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet, '```charty')
    writeline(uptime_sheet, '{')
    writeline(uptime_sheet, '  "title":   "🔎 Groups Monitored",')
    writeline(uptime_sheet, '  "caption": "",')
    writeline(uptime_sheet, '  "type":    "review",')
    writeline(uptime_sheet, '  "options": {')
    writeline(uptime_sheet, '    "legend":  true,')
    writeline(uptime_sheet, '    "labels":  true,')
    writeline(uptime_sheet, '    "numbers": true')
    writeline(uptime_sheet, '  },')
    writeline(uptime_sheet, '  "data": [')
    writeline(uptime_sheet, '      { "label": "📡 Relays & mirrors", "value": ' + str(hostcount()) + '},')
    writeline(uptime_sheet, '      { "label": "🏴‍☠️  Groups", "value": ' + str(groupcount()) + '},')
    writeline(uptime_sheet, '      { "label": "🟢 Online", "value": ' + str(onlinecount()) + ' }')
    writeline(uptime_sheet, '  ]')
    writeline(uptime_sheet, '}')
    writeline(uptime_sheet, '```')
    writeline(uptime_sheet, '```charty')
    writeline(uptime_sheet, '{')
    writeline(uptime_sheet, '  "title":   "📆 Victims detected",')
    writeline(uptime_sheet, '  "caption": "",')
    writeline(uptime_sheet, '  "type":    "review",')
    writeline(uptime_sheet, '  "options": {')
    writeline(uptime_sheet, '    "legend":  true,')
    writeline(uptime_sheet, '    "labels":  true,')
    writeline(uptime_sheet, '    "numbers": true')
    writeline(uptime_sheet, '  },')
    writeline(uptime_sheet, '  "data": [')
    writeline(uptime_sheet, '      { "label": "Last 24 hours", "value": ' + str(postslast24h()) + '},')
    writeline(uptime_sheet, '      { "label": "Last 7 days", "value": ' + str(postssince(7)) + '},')
    writeline(uptime_sheet, '      { "label": "Last 30 days", "value": ' + str(postssince(30)) + '},')
    current_year = datetime.now().year
    yearminusone = current_year - 1 
    yearminustwo = current_year - 2 
    writeline(uptime_sheet, '      { "label": "In ' +  str(current_year) + '", "value": ' + str(postsyear(current_year)) + '},')
    writeline(uptime_sheet, '      { "label": "In ' +  str(yearminusone) + '", "value": ' + str(postsyear(yearminusone)) + '},')
    writeline(uptime_sheet, '      { "label": "In ' +  str(yearminustwo) + '", "value": ' + str(postsyear(yearminusone)) + '}')
    writeline(uptime_sheet, '  ]')
    writeline(uptime_sheet, '}')
    writeline(uptime_sheet, '```')
    writeline(uptime_sheet, '📸 There are `' +  str(screenshots) + '` ransomware group host screenshots and `' + str(nbscreenshots) + '` victims screenshots')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '📝 There are `' +  str(nbransom_notes) + '` ransomware notes and `' + str(nbsnego) +'` negotiation chats')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '🕵🏻‍♂️ There are `' + str(nbsinfostealer) + '`victims which have been compromised by infostealer')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '⚙️ Ransomware.live has `' + str(parsercount()) + '` active parsers for indexing victims')
    writeline(uptime_sheet, '')
    if os.getenv('API_LOG',False):
        stdlog('Get API log')
        writeline(uptime_sheet, '🔎 Ransomware.live is being queried by `' + str(count_OpenCTI(os.getenv('API_LOG'))) + '` instances of [OpenCTI](https://filigran.io/solutions/open-cti/)')
        writeline(uptime_sheet, '')
    writeline(uptime_sheet, 'So far, Ransomware.live has indexed `' + str(postcount()) + '` victims')
    with open(VICTIMS_FILE) as file:
        data = json.load(file)
    # Filter the posts for the year 2023
    filtered_data = [post for post in data if post.get('published', '').startswith(str(current_year))]
    # Extract the group names from the filtered data
    group_names = [post['group_name'] for post in filtered_data]
    # Calculate the number of unique groups
    num_unique_groups = len(set(group_names))
    # Count the occurrences of each group name
    group_counts = Counter(group_names)
    # Get the top 10 groups with their counts
    top_groups = group_counts.most_common(10)
    total_posts = len(group_names)
    # Calculate the count for the "Other" group
    other_count = total_posts - sum(count for _, count in top_groups)
    writeline(uptime_sheet, '```charty')
    writeline(uptime_sheet, '{')
    writeline(uptime_sheet,'  "title":   "🏆 Top 10 Ranwomware groups for ' + str(current_year) +'",')
    writeline(uptime_sheet, '  "caption": "based on our database",')
    writeline(uptime_sheet, '  "type":    "doughnut",')
    writeline(uptime_sheet, '  "options": {')
    writeline(uptime_sheet, '    "legend":  true,')
    writeline(uptime_sheet, '    "labels":  true,')
    writeline(uptime_sheet, '    "numbers": true')
    writeline(uptime_sheet, '  },')
    writeline(uptime_sheet, '  "data": [')

    for group, count in top_groups:
            writeline(uptime_sheet, '{ "label": "' + group + '", "value": '+ str(count) + '},')
    writeline(uptime_sheet, '{ "label": "Others", "value": '+ str(other_count) + '}')
    writeline(uptime_sheet, '   ]')
    writeline(uptime_sheet, '}')
    writeline(uptime_sheet, '```')
    writeline(uptime_sheet,' ')
    writeline(uptime_sheet,'<a href="https://www.buymeacoffee.com/ransomwarelive" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>')

    writeline(uptime_sheet, '')
    writeline(uptime_sheet, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    writeline(uptime_sheet, '')


###################
### STATUS PAGE ###
###################
def statuspage():
    index_sheet = 'docs/status.md'
    with open(index_sheet, 'w', encoding='utf-8') as f:
        f.close()
    groups = openjson(GROUPS_FILE)
    writeline(index_sheet, '')
    writeline(index_sheet, '## 🚦 All Groups')
    writeline(index_sheet, '')
    header = '| Group | Title | Status | Last seen | Location | Screenshot |'
    writeline(index_sheet, header)
    writeline(index_sheet, '|---|---|---|---|---|---|')
    for group in groups:
        for host in group['locations']:
            if host['available'] is True:
                statusemoji = '🟢'
                lastseen = ''
            elif host['available'] is False:
                # iso timestamp converted to yyyy/mm/dd
                lastseen = host['lastscrape'].split(' ')[0]
                statusemoji = '🔴'
            if host['title'] is not None:
                title = host['title'].replace('|', '-')
            else:
                title = ''
            screenshot=host['fqdn'].replace('.', '-') + '.png'
            screen=''
            if os.path.exists('docs/screenshots/'+screenshot):
                screen='<a href="https://images.ransomware.live/screenshots/' + screenshot + '" target=_blank>📸</a>'
            line = '| [' + group['name'] + '](group/' + group['name'] + ') | ' + clean_string(title)+ ' | ' + statusemoji + ' | ' + lastseen + ' | ' + host['fqdn'] + ' | ' + screen + ' | ' 
            writeline(index_sheet, line)
    writeline(index_sheet, '')
    writeline(index_sheet, '---')
    writeline(index_sheet, '')
    writeline(index_sheet, '## 🟢 Online Groups')
    writeline(index_sheet, '')
    header = '| Group | Title | Location | Screenshoot |'
    writeline(index_sheet, header)
    writeline(index_sheet, '|---|---|---|---|')
    for group in groups:
        for host in group['locations']:
            if host['available'] is True:
                if host['title'] is not None:
                    title = host['title'].replace('|', '-')
                else:
                    title = ''
                screenshot=host['fqdn'].replace('.', '-') + '.png'
                screen=''
                if os.path.exists('docs/screenshots/'+screenshot):
                    screen = '<a href="https://images.ransomware.live/screenshots/' + screenshot + '" target=_blank>📸</a>'
                line = '| [' + group['name'] + '](group/' + group['name'] + ') | ' + title + ' | ' + host['fqdn'] + ' | ' + screen + ' | ' 
                writeline(index_sheet, line)
    writeline(index_sheet, '')
    #writeline(index_sheet, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    writeline(index_sheet, '')

###########################
### RECENT VICTIMS PAGE ###
###########################
def recentattackedpage():
    '''create a markdown table for the last 200 posts based on the published value'''
    fetching_count = 200
    stdlog('Generating recent attacked victims page')
    recentpage = 'docs/recentattackedvictims.md'
    with open(recentpage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(recentpage,'# Recent victims by Ransomware.live')
    writeline(recentpage,'')
    writeline(recentpage, '> [!INFO] `Ransomware.live` provides tracking of ransomware groups and their victims. Descriptions available in the [group profiles view](profiles.md)')
    writeline(recentpage, '> ')
    writeline(recentpage, '> *Legend:*')
    writeline(recentpage, '> ')
    writeline(recentpage, '>    📸  *Screenshot of the ransomware victim\'s post*')
    writeline(recentpage, '> ')
    writeline(recentpage, '>    🕵🏻‍♂️  *Information about infostealer for the victim. Provided by [HudsonRock](https://www.hudsonrock.com)* ')
    writeline(recentpage,'')
    writeline(recentpage, '**📰 200 last victims sorted by discovered date by `Ransomware.live`**')
    writeline(recentpage, '')
    writeline(recentpage, '| Attacked Date | [Discovered Date](recent.md) | Victim | [Country](country) | Group | 📸 | 🕵🏻‍♂️ | ')
    writeline(recentpage, '|---|---|---|---|---|---|---|')
    for post in recentattackedposts(fetching_count):
        # show friendly date for discovered
        date = post['discovered'].split(' ')[0]
        attack = post['published'].split(' ')[0]
        attacked_date = post.get('attacked_date', None)
        if attacked_date:
            attack = attacked_date.split(' ')[0]
        elif (attack == date):
            attack =''
        # replace markdown tampering characters
        title = post['post_title'].replace('|', '-').replace('&amp;','&').replace('amp;','')
        group = post['group_name'].replace('|', '-')
        urlencodedtitle = urllib.parse.quote_plus(title)
        grouplink = '[' + group + '](group/' + group + ')'
        # screenpost='❌'
        screenpost=' '
        if post['post_url'] is not None: 
            # Create an MD5 hash object
            hash_object = hashlib.md5()
            # Update the hash object with the string
            hash_object.update(post['post_url'].encode('utf-8'))
            # Get the hexadecimal representation of the hash
            hex_digest = hash_object.hexdigest()
            if os.path.exists('docs/screenshots/posts/'+hex_digest+'.png'):
                screenpost='<a href="https://images.ransomware.live/screenshots/posts/' + hex_digest + '.png" target=_blank>👀</a>'
            if len(post['country']) > 1:
                flag = post['country']
                country="[!["+flag+"](https://images.ransomware.live/flags/"+flag+".svg ':size=32x24 :no-zoom')](country/"+flag.lower()+")"
            else:
                country=''
            hash_object = hashlib.md5()
            # Update the hash object with the string
            hash_object.update(title.lower().encode('utf-8'))
            # Get the hexadecimal representation of the hash
            hex_digest = hash_object.hexdigest()
            if os.path.exists('docs/domain/'+hex_digest+'.md'):
                infostealer=' [🔎](domain/'+hex_digest+') '
            elif post['website']:
                domain = extract_domain(post['website'].lower()) #.replace('http://','').replace('https://','').replace('www.','')
                hash_object = hashlib.md5()
                hash_object.update(domain.encode('utf-8'))
                hex_digest = hash_object.hexdigest()
                if  os.path.exists('docs/domain/'+hex_digest+'.md'):
                    infostealer=' [🔎](domain/'+hex_digest+') '
                else:
                    infostealer = ''
            else:
                infostealer = ''
        if attack == '':
            attack=date 
        if attack == date:
            date = ''
        #line = '| ' + date + ' | [`' + title + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + grouplink + ' | ' + screenpost + ' |'
        line = '| ' + attack + ' | ' + date + ' | [`' + title + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + country + ' | ' + grouplink + ' | ' + screenpost + ' | ' + infostealer + ' |'
        result = get_removal(title, group)
        if result:  
             line = '| ' + date + ' | ' + attack + ' | *' + result + '* | ' + country + ' | ' + grouplink + ' |   |   |'
        writeline(recentpage, line)
    writeline(recentpage, '')
    writeline(recentpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('recent published victims page generated')


def recentdiscoveredpage():
    '''create a markdown table for the last 200 posts based on the published value'''
    fetching_count = 200
    stdlog('Generating recent discovered victims page')
    recentpage = 'docs/recent.md'
    with open(recentpage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(recentpage,'# Recent victims by Ransomware.live')
    writeline(recentpage,'')
    writeline(recentpage, '> [!INFO] `Ransomware.live` provides tracking of ransomware groups and their victims. Descriptions available in the [group profiles view](profiles.md)')
    writeline(recentpage, '> ')
    writeline(recentpage, '> *Legend:*')
    writeline(recentpage, '> ')
    writeline(recentpage, '>    📸  *Screenshot of the ransomware victim\'s post*')
    writeline(recentpage, '> ')
    writeline(recentpage, '>    🕵🏻‍♂️  *Information about infostealer for the victim. Provided by [HudsonRock](https://www.hudsonrock.com)* ')
    writeline(recentpage,'')
    writeline(recentpage, '**📰 200 last victims sorted by discovered date by `Ransomware.live`**')
    writeline(recentpage, '')
    writeline(recentpage, '| Discovery Date | [Attack Date](recentattackedvictims.md) | Victim | [Country](country) | Group | 📸 | 🕵🏻‍♂️ | ')
    writeline(recentpage, '|---|---|---|---|---|---|---|')
    for post in recentdiscoveredposts(fetching_count):
        # show friendly date for discovered
        date = post['discovered'].split(' ')[0]
        attack = post['published'].split(' ')[0]
        attacked_date = post.get('attacked_date', None)
        if attacked_date:
            attack = attacked_date.split(' ')[0]
        elif (attack == date):
            attack =''
        # replace markdown tampering characters
        title = post['post_title'].replace('|', '-').replace('&amp;','&').replace('amp;','')
        group = post['group_name'].replace('|', '-')
        urlencodedtitle = urllib.parse.quote_plus(title)
        grouplink = '[' + group + '](group/' + group + ')'
        # screenpost='❌'
        screenpost=' '
        if post['post_url'] is not None: 
            # Create an MD5 hash object
            hash_object = hashlib.md5()
            # Update the hash object with the string
            hash_object.update(post['post_url'].encode('utf-8'))
            # Get the hexadecimal representation of the hash
            hex_digest = hash_object.hexdigest()
            if os.path.exists('docs/screenshots/posts/'+hex_digest+'.png'):
                screenpost='<a href="https://images.ransomware.live/screenshots/posts/' + hex_digest + '.png" target=_blank>👀</a>'
            if len(post['country']) > 1:
                flag = post['country']
                country="[!["+flag+"](https://images.ransomware.live/flags/"+flag+".svg ':size=32x24 :no-zoom')](country/"+flag.lower()+")"
            else:
                country=''
            hash_object = hashlib.md5()
            # Update the hash object with the string
            hash_object.update(title.replace('www.','').lower().encode('utf-8'))
            # Get the hexadecimal representation of the hash
            hex_digest = hash_object.hexdigest()
            if os.path.exists('docs/domain/'+hex_digest+'.md'):
                infostealer=' [🔎](domain/'+hex_digest+') '
            elif post['website']:
                domain = extract_domain(post['website'].lower()).strip()  #.replace('http://','').replace('https://','').replace('www.','')
                hash_object = hashlib.md5()
                hash_object.update(domain.encode('utf-8'))
                hex_digest = hash_object.hexdigest()
                if  os.path.exists('docs/domain/'+hex_digest+'.md'):
                    infostealer=' [🔎](domain/'+hex_digest+') '
                else:
                    infostealer = ''
            else:
                infostealer = ''
        line = '| ' + date + ' | ' + attack + ' | [`' + clean_string(title) + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + country + ' | ' + grouplink + ' | ' + screenpost + ' | ' + infostealer + ' |'
        result = get_removal(title, group)
        if result:  
             line = '| ' + date + ' | ' + attack + ' | *' + result + '* | ' + country + ' | ' + grouplink + ' |   |   |'
        writeline(recentpage, line)
    writeline(recentpage, '')
    writeline(recentpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('recent published victims page generated')


#############################
### LAST VICTIM PER GROUP ###
#############################
def lastvictimspergroup():
    stdlog('generating last victim per group')
    page = 'docs/lastvictimspergroup.md'
    index_sheet = 'docs/status.md'
    with open(page, 'w', encoding='utf-8') as f:
        f.close()
    # Load the data from the JSON files
    groups = openjson(GROUPS_FILE)
    victims = openjson(VICTIMS_FILE)
    # Create a dictionary to store the last post information for each group
    last_posts_info = {}

    # Calculate date thresholds
    today = datetime.now().date()

    # Process each group and find the last post title, website, and published date
    for group in groups:
        group_name = group['name']
        
        # Find the latest post for the group based on discovery timestamp
        latest_post = None
        for victim in victims:
            if victim['group_name'] == group_name:
                if latest_post is None or victim['discovered'] > latest_post['discovered']:
                    latest_post = victim
        
        if latest_post:
            website = latest_post.get('website', None)  # Get the website if available
            
            # Check if the website starts with http:// or https://
            if website and not website.startswith(('http://', 'https://')):
                website = f'http://www.{website}'
            elif website and website.startswith('https://'):
                website = website.replace('https://', 'http://www.')
            elif website and website.startswith('http://'):
                website = website.replace('http://', 'http://www.')
            

            # Parse the published date and compare with date thresholds
            published_date = datetime.strptime(latest_post['published'], '%Y-%m-%d %H:%M:%S.%f').date()
            days_difference = (today - published_date).days
            date_status = "🟢"
            if days_difference > 90:
                date_status = "🟠"
            if days_difference > 180:
                date_status = "🔴"

            
            last_posts_info[group_name] = {
                'last_post_title': latest_post['post_title'],
                'published_date': latest_post['published'].split()[0],  # Extract only the date part
                'website': website,
                'date_status' : date_status
            }
    writeline(page, '',index_sheet)
    writeline(page, '## 🎯 Last victim per Group',index_sheet)
    writeline(page, '',index_sheet)
    writeline(page, '',index_sheet)
    writeline(page, '| Ransomware | Last Victim | Date | Status[<sup>*</sup>](lastvictimspergroup?id=-legend-) |',index_sheet)
    writeline(page, '|---|---|---|---|',index_sheet)
    # Print the last post title, published date, and website for each group with a last post
    for group_name, info in last_posts_info.items():
        if info['last_post_title'] != "No posts found": 
            if info['website']:
                website = info['website']
            else:
                search_query = urllib.parse.quote(info['last_post_title'])
                google_search_url = f"https://www.google.com/search?q={search_query}"
                website =  google_search_url
            writeline(page, '| [`' + group_name + '`](group/' + group_name +') |  ['+ info['last_post_title'] + '](' + website+ ') |' + info['published_date'] + ' |' + info['date_status'] + '|',index_sheet)
    writeline(page, '',index_sheet)
    writeline(page, '### <u> Legend : </u>  ',index_sheet)
    writeline(page, '',index_sheet)
    writeline(page, '🟢  less 3 months old',index_sheet)
    writeline(page, '',index_sheet)
    writeline(page, '🟠  between 3 months and 6 months old',index_sheet)
    writeline(page, '',index_sheet)
    writeline(page, '🔴  older than 6 months',index_sheet)
    writeline(page, '',index_sheet)
    writeline(page, '',index_sheet)
    writeline(page, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_',index_sheet)
    stdlog('Last victim per ransomware page generated')

###################################
### PROFILE PAGE FOR EACH GROUP ###
###################################
def profilepage():
    '''
    create a profile page with each group in their unique markdown files within docs/profiles
    '''
    stdlog('generating profile pages')
    profilepage = 'docs/profiles.md'
    # delete contents of file
    with open(profilepage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(profilepage, '')
    writeline(profilepage, '# All Groups')
    writeline(profilepage, '')
    writeline(profilepage, '> [Last victim per Ransomware group](lastvictimspergroup.md)')
    writeline(profilepage, '')
    groups = openjson(GROUPS_FILE)
    groupcpt=0
    for group in groups:
        writeline(profilepage, '## **' + group['name']+'**')
        writeline(profilepage,'')
        writeline(profilepage,'')
        if 'description' in group:
            if group['description']:
                writeline(profilepage,'>[!INFO]')
                writeline(profilepage,'> ' + group['description'])
                writeline(profilepage, '')
        writeline(profilepage, '')
        if group['meta'] is not None:
            writeline(profilepage, '_`' + group['meta'] + '`_')
            writeline(profilepage, '')
        if group['parser']:
            writeline(profilepage,'')
            writeline(profilepage,'🔎 `ransomware.live`has an active  parser for indexing '+ group['name']+'\'s victims')
            writeline(profilepage, '') 
        writeline(profilepage, '')
        writeline(profilepage, '<!-- tabs:start -->') 
        writeline(profilepage, '#### **URLs**')
        writeline(profilepage, '| Title | Available | Last visit | fqdn | Screenshot ')
        writeline(profilepage, '|---|---|---|---|---|')        
        for host in group['locations']:
            if host['available'] is True:
                statusemoji = '🟢'
            elif host['available'] is False:
                statusemoji = '🔴'
            # convert date to ddmmyyyy hh:mm
            date = host['lastscrape'].split(' ')[0]
            date = date.split('-')
            date = date[2] + '/' + date[1] + '/' + date[0]
            time = host['lastscrape'].split(' ')[1]
            time = time.split(':')
            time = time[0] + ':' + time[1]
            screenshot=host['fqdn'].replace('.', '-') + '.png'
            screen='❌'
            if os.path.exists('docs/screenshots/'+screenshot):
                screen='<a href="https://images.ransomware.live/screenshots/' + screenshot + '" target=_blank>📸</a>'
            if host['title'] is not None:
                line = '| ' + host['title'].replace('|', '-') + ' | ' + statusemoji +  ' | ' + date + ' ' + time + ' | `http://' + host['fqdn'] + '` | ' + screen + ' | ' 
                writeline(profilepage, line)
            else:
                line = '| none | ' + statusemoji +  ' | ' + date + ' ' + time + ' | `http://' + host['fqdn'] + '` | ' + screen + ' | ' 
                writeline(profilepage, line)
        if len(group['profile']):
            writeline(profilepage, '#### **External information**')
            for profile in group['profile']:
                writeline(profilepage, '- ' + profile)
                writeline(profilepage, '')
            writeline(profilepage, '')
            writeline(profilepage, '> provided by [Ransomware-Tool-Matrix](https://github.com/BushidoUK/Ransomware-Tool-Matrix)')
            writeline(profilepage, '')
                
        cpt_note = 0 
        directory = 'docs/ransomware_notes/' + group['name'] +'/'
        if directory_exists(directory):
            for filename in sorted(os.listdir(directory)):
                cpt_note += 1
            writeline(profilepage, '')        
        if cpt_note > 0:
            if cpt_note > 1:
                pluriel='s'
            else:
                pluriel=''
            writeline(profilepage, '')
            writeline(profilepage, '#### **Ransom note**')
            writeline(profilepage,'* [📝 ' +  str(cpt_note) + ' ransom note' + pluriel + '](notes/'+ group['name'] + ')')
        if os.path.exists('docs/crypto/'+group['name']+'.md'):
            ### Crypto 
            writeline(profilepage, '')
            writeline(profilepage, '#### **Crypto Wallet**')
            writeline(profilepage, '* 💰 <a href="/#/crypto/'+group['name']+'.md">Crypto wallet(s) available</a>')
            writeline(profilepage, '')
        
         ### NEGO
        nego = group['name']
        if group['name'] == 'lockbit3':
            nego='lockbit3.0'
        if group['name'] == 'ragnarlocker':
            nego='ragnar-locker'
        directory = '/var/www/ransomware.live/docs/negotiation/' + nego +'/'
        if directory_exists(directory):
            writeline(profilepage, '')
            writeline(profilepage, '#### ** Negotiation chats**')
            writeline(profilepage, '')
            writeline(profilepage, '| Name | Link |')
            writeline(profilepage, '|---|---|')
            for filename in sorted(os.listdir(directory)):
                line = '|' + os.path.splitext(filename)[0].replace('_','.') + '|  <a href="/#/negotiation/' + nego + '/' + filename + '"> 💬 </a> |'
                writeline(profilepage, line)
            writeline(profilepage, '')
        writeline(profilepage, '<!-- tabs:end -->')
        
        ### GRAPH
        if os.path.exists('docs/graphs/stats-'+group['name']+'.png'):
            writeline(profilepage, '')
            writeline(profilepage, '### _Total Attacks Over Time_')
            writeline(profilepage, '')
            writeline(profilepage,'![Statistics](/graphs/stats-' + group['name'] + '.png)') 
            writeline(profilepage, '')

        ### POSTS 
        writeline(profilepage, '')
        writeline(profilepage, '### _Victims_')
        writeline(profilepage, '')
        writeline(profilepage, '> ' + grouppostcount(group['name']))
        writeline(profilepage, '')
        if grouppostavailable(group['name']):
            writeline(profilepage, '| victim | date | Description | Screenshot | ')
            writeline(profilepage, '|---|---|---|---|')
            posts = openjson(VICTIMS_FILE)
            sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
            filtered_posts = [post for post in sorted_posts if post['group_name'] == group['name']]
            last_10_posts = filtered_posts[:10]

            for post in last_10_posts:
                    if 'description' in post:
                        description = redactedlink(post['description'])
                    else:
                        description = ' '
                    description = clean_markdown(description)
                    try:
                        if post['website'] == "": 
                            urlencodedtitle = urllib.parse.quote_plus(post['post_title'])
                            postURL = '[`' + post['post_title'].replace('|', '') + '`](https://google.com/search?q=' + urlencodedtitle  + ')'
                        else: 
                            if 'http' in post['website']:                       
                                postURL = '[`' + post['post_title'].replace('|', '') + '`](' + post['website'] + ')'
                            else:
                                postURL = '[`' + post['post_title'].replace('|', '') + '`](https://' + post['website'] + ')'
                    except: 
                        urlencodedtitle = urllib.parse.quote_plus(post['post_title'])
                        postURL = '[`' + post['post_title'].replace('|', '') + '`](https://google.com/search?q=' + urlencodedtitle  + ')'
                    date = post['published'].split(' ')[0]
                    try:
                        datetime.strptime(date, '%Y-%m-%d')
                    except ValueError:
                        date = post['discovered'].split(' ')[0]
                    date = date.split('-')
                    date = date[2] + '/' + date[1] + '/' + date[0]
                    screenpost=' '
                    if post['post_url'] is not None: 
                        # Create an MD5 hash object
                        hash_object = hashlib.md5()
                        # Update the hash object with the string
                        hash_object.update(post['post_url'].encode('utf-8'))
                        # Get the hexadecimal representation of the hash
                        hex_digest = hash_object.hexdigest()
                        if os.path.exists('docs/screenshots/posts/'+hex_digest+'.png'):
                            screenpost='<a href="https://images.ransomware.live/screenshots/posts/' + hex_digest + '.png" target=_blank>📸</a>'
                    line = '| ' + postURL + ' | ' + date + ' | ' + description + ' | ' + screenpost + ' |'
                    result = get_removal(post['post_title'], post['group_name'])
                    if result:  
                        line = '| *' + result + '* | ' + date + ' |  |  |'
                    writeline(profilepage, line)
        writeline(profilepage, '')
        if  postcountgroup(group['name']) > 10:
            writeline(profilepage, '↪️ More victims [here](/group/' + group['name'] + '?id=posts)')
            writeline(profilepage, '')
        writeline(profilepage,' --- ')
        writeline(profilepage, '')
        groupcpt +=1
        stdlog('[' + str(groupcpt) + '/' + str(groupcount()) + '] Added ' + group['name'] + ' to all profiles page')
    writeline(profilepage, '')
    writeline(profilepage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('profile page generation complete')




def allposts():
    '''create a markdown table for all posts '''
    stdlog('generating allvictims page')
    allpage = 'docs/allvictims.md'
    # delete contents of file
    with open(allpage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(allpage, '')
    writeline(allpage, '# All victims')
    writeline(allpage, '')
    writeline(allpage, '_All `' + str(postcount()) + '` posts_')
    writeline(allpage, '')
    writeline(allpage, '') 
    writeline(allpage, '💾 [Download](https://data.ransomware.live/victims.json) full list in **json** format')
    writeline(allpage, '')
    writeline(allpage, '💾 [Download](https://www.ransomware.live/victims.csv) full list in **csv** format')
    writeline(allpage, '')
    writeline(allpage, '')
    writeline(allpage, '| Discovery Date | Attack Date | Victim | [Country](country) | Group | 📸 | 🕵🏻‍♂️ | ')
    writeline(allpage, '|---|---|---|---|---|---|---|')
    posts = openjson(VICTIMS_FILE)
    sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
    for post in sorted_posts:
       # show friendly date for discovered
        date = post['discovered'].split(' ')[0]
        attack = post['published'].split(' ')[0]
        if (attack == date):
            attack =''
        # replace markdown tampering characters
        title = post['post_title'].replace('|', '-')
        group = post['group_name'].replace('|', '-')
        urlencodedtitle = urllib.parse.quote_plus(title)
        grouplink = '[' + group + '](group/' + group + ')'
        # screenpost='❌'
        screenpost=' '
        if post['post_url'] is not None: 
            # Create an MD5 hash object
            hash_object = hashlib.md5()
            # Update the hash object with the string
            hash_object.update(post['post_url'].encode('utf-8'))
            # Get the hexadecimal representation of the hash
            hex_digest = hash_object.hexdigest()
            if os.path.exists('docs/screenshots/posts/'+hex_digest+'.png'):
                screenpost='<a href="https://images.ransomware.live/screenshots/posts/' + hex_digest + '.png" target=_blank>👀</a>'
            if len(post['country']) > 1:
                flag = post['country']
                country="[!["+flag+"](https://images.ransomware.live/flags/"+flag+".svg ':size=32x24 :no-zoom')](country/"+flag.lower()+")"
            else:
                country=''
            hash_object = hashlib.md5()
            # Update the hash object with the string
            hash_object.update(title.replace('www.','').lower().encode('utf-8'))
            # Get the hexadecimal representation of the hash
            hex_digest = hash_object.hexdigest()
            try:
                if os.path.exists('docs/domain/'+hex_digest+'.md'):
                    infostealer=' [🔎](domain/'+hex_digest+') '
                elif post['website']:
                    domain = extract_domain(post['website'].lower()) #.replace('http://','').replace('https://','').replace('www.','')
                    hash_object = hashlib.md5()
                    hash_object.update(domain.encode('utf-8'))
                    hex_digest = hash_object.hexdigest()
                    if  os.path.exists('docs/domain/'+hex_digest+'.md'):
                        infostealer=' [🔎](domain/'+hex_digest+') '
                    else:
                        infostealer = ''
                else:
                    infostealer = ''
            except:
                infostealer = '' 
        line = '| ' + date + ' | ' + attack + ' | [`' + title + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + country + ' | ' + grouplink + ' | ' + screenpost + ' | ' + infostealer + ' |'
        result = get_removal(title, group)
        if result:  
             line = '| ' + date + ' | ' + attack + ' | *' + result + '* | ' + country + ' | ' + grouplink + ' |   |   |'
        writeline(allpage, line)
    writeline(allpage, '')
    writeline(allpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('all posts page generated')





#######################################
### CREATE A PROFILE PAGE PER GROUP ###
#######################################
def groupprofilepage():
    '''
    create a profile page for each group in their unique markdown files within docs/profiles
    '''
    groups = openjson(GROUPS_FILE)
    stdlog('generating profile pages for groups')
    groupcpt=0
    for group in groups:
        profilepage = 'docs/group/' + group['name'] + '.md'
        # delete contents of file
        with open(profilepage, 'w', encoding='utf-8') as f:
            f.close()
        writeline(profilepage, '# Profile for ransomware group : **' + group['name']+'**')
        writeline(profilepage, '')
        writeline(profilepage, '')
        if 'description' in group:
            if group['description']:
                writeline(profilepage,'>[!INFO]')
                writeline(profilepage,'> ' + group['description'])
                writeline(profilepage, '')
        writeline(profilepage, '')
        writeline(profilepage, '')
        ## add notes if present
        #if group['meta'] is not None:  
        #    writeline(profilepage, '_`' + group['meta'] + '`_')
        #    writeline(profilepage, '')
        if group['parser']:
            writeline(profilepage,'')
            writeline(profilepage,'🔎 `ransomware.live`has an active parser for indexing '+ group['name']+'\'s victims')
            writeline(profilepage, '')  
        if os.path.exists(f"docs/ttps/{group['name']}.md"):
            writeline(profilepage, '')
            writeline(profilepage, f"🛠️ [Tools used by {group['name']}](ttps/{group['name']}.md)")
            writeline(profilepage, '')
        if len(group['profile']):
            writeline(profilepage, '### External analysis')
            for profile in group['profile'][:10]:
                writeline(profilepage, '- ' + profile)
                writeline(profilepage, '')
            writeline(profilepage, '')
            writeline(profilepage, '> provided by [Ransomware-Tool-Matrix](https://github.com/BushidoUK/Ransomware-Tool-Matrix)')
            writeline(profilepage, '')
        writeline(profilepage, '### URLs')
        writeline(profilepage, '| Title | Available | Last visit | fqdn | Screenshot ')
        writeline(profilepage, '|---|---|---|---|---|')        
        for host in group['locations']:
            if host['available'] is True:
                statusemoji = '🟢'
            elif host['available'] is False:
                statusemoji = '🔴'
            # convert date to ddmmyyyy hh:mm
            date = host['lastscrape'].split(' ')[0]
            date = date.split('-')
            date = date[2] + '/' + date[1] + '/' + date[0]
            time = host['lastscrape'].split(' ')[1]
            time = time.split(':')
            time = time[0] + ':' + time[1]
            screenshot=host['fqdn'].replace('.', '-') + '.png'
            screen='❌'
            if os.path.exists('docs/screenshots/'+screenshot):
                screen='<a href="https://images.ransomware.live/screenshots/' + screenshot + '" target=_blank>📸</a>'
            if host['title'] is not None:
                line = '| ' + host['title'].replace('|', '-') + ' | ' + statusemoji +  ' | ' + date + ' ' + time + ' | `http://' + host['fqdn'] + '` | ' + screen + ' | ' 
                writeline(profilepage, line)
            else:
                line = '| none | ' + statusemoji +  ' | ' + date + ' ' + time + ' | `http://' + host['fqdn'] + '` | ' + screen + ' | ' 
                writeline(profilepage, line)
        cpt_note = 0 
        directory = 'docs/ransomware_notes/' + group['name'] +'/'
        if directory_exists(directory):
            for filename in sorted(os.listdir(directory)):
                cpt_note += 1
            writeline(profilepage, '')        
        if cpt_note > 0:
            if cpt_note > 1:
                pluriel='s'
            else:
                pluriel='' 
            writeline(profilepage, '')
            writeline(profilepage, '### Ransom note')
            writeline(profilepage,'* [📝 ' +  str(cpt_note) + ' ransom note' + pluriel + '](notes/'+ group['name'] + ')')
        if os.path.exists('docs/crypto/'+group['name']+'.md'):
            ### Crypto 
            writeline(profilepage, '')
            writeline(profilepage, '### Crypto wallets')
            writeline(profilepage, '* 💰 <a href="/#/crypto/'+group['name']+'.md">Crypto wallet(s) available</a>')
            writeline(profilepage, '')

        ### NEGO
        nego = group['name']
        if group['name'] == 'lockbit3':
            nego='lockbit3.0'
        if group['name'] == 'ragnarlocker':
            nego='ragnar-locker'
        directory = './docs/negotiation/' + nego +'/'
        if directory_exists(directory):
            writeline(profilepage, '')
            writeline(profilepage, '### Negotiation chats')
            writeline(profilepage, '')
            writeline(profilepage, '| Name | Link |')
            writeline(profilepage, '|---|---|')
            for filename in sorted(os.listdir(directory)):
                line = '|' + os.path.splitext(filename)[0] + '|  <a href="/#/negotiation/' + nego + '/' + filename + '"> 💬 </a> |'
                writeline(profilepage, line)
            writeline(profilepage, '')

        
        with open('./data/tidalcyber-ttps.json', 'r') as file:
            data = json.load(file)

            # Define the specific ransomwatch_threat you want to find
            target_threat = group['name']


            # Search for the threat and retrieve its ttps value
            ttps_value = None
            for entry in data:
                if entry['ransomwatch_threat'] == target_threat:
                    ttps_value = entry['ttps']
                    writeline(profilepage,'')
                    writeline(profilepage,'### Technique Set')
                    writeline(profilepage,'')
                    writeline(profilepage,'* 🛠️ A technique set is [available](' + ttps_value + ') from [Tidal Cyber](https://www.tidalcyber.com/)')
                    writeline(profilepage,'')

        ### GRAPH
        if os.path.exists('docs/graphs/stats-'+group['name']+'.png'):
            writeline(profilepage, '')
            writeline(profilepage, '### Total Attacks Over Time')
            writeline(profilepage, '')
            writeline(profilepage,'![Statistics](../graphs/stats-' + group['name'] + '.png)') 
            writeline(profilepage, '')

        ### POSTS 
        writeline(profilepage, '')
        writeline(profilepage, '### Victims')
        writeline(profilepage, '')
        writeline(profilepage, '> ' + grouppostcount(group['name']))
        writeline(profilepage, '')
        if grouppostavailable(group['name']):
            if group['name'] == 'bianlian' or group['name'] == 'cloak':
                writeline(profilepage, '| victim | date | Description | Possible victim | Screenshot | 🕵🏻‍♂️ |')
                writeline(profilepage, '|---|---|---|---|---|---|')
            else:
                writeline(profilepage, '| victim | date | Description | Screenshot | 🕵🏻‍♂️ |')
                writeline(profilepage, '|---|---|---|---|---|')
            posts = openjson(VICTIMS_FILE)
            sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
            for post in sorted_posts:
                if post['group_name'] == group['name']:
                    if 'description' in post:
                        description = redactedlink(post['description'])
                    else:
                        description = ' '
                    description = clean_markdown(description)
                    try:
                        if post['website'] == "": 
                            urlencodedtitle = urllib.parse.quote_plus(post['post_title'])
                            postURL = '[`' + post['post_title'].replace('|', '') + '`](https://google.com/search?q=' + urlencodedtitle  + ')'
                        else: 
                            if 'http' in post['website']:                       
                                postURL = '[`' + post['post_title'].replace('|', '') + '`](' + post['website'].replace(' ','%20') + ')'
                            else:
                                postURL = '[`' + post['post_title'].replace('|', '') + '`](https://' + post['website'].replace(' ','%20') + ')'
                    except: 
                        urlencodedtitle = urllib.parse.quote_plus(post['post_title'])
                        postURL = '[`' + post['post_title'].replace('|', '') + '`](https://google.com/search?q=' + urlencodedtitle  + ')'
                    date = post['published'].split(' ')[0]
                    try:
                        datetime.strptime(date, '%Y-%m-%d')
                    except ValueError:
                        date = post['discovered'].split(' ')[0]
                    date = date.split('-')
                    date = date[2] + '/' + date[1] + '/' + date[0]
                    screenpost=' '
                    if post['post_url'] is not None: 
                        # Create an MD5 hash object
                        hash_object = hashlib.md5()
                        # Update the hash object with the string
                        hash_object.update(post['post_url'].encode('utf-8'))
                        # Get the hexadecimal representation of the hash
                        hex_digest = hash_object.hexdigest()
                        if os.path.exists('docs/screenshots/posts/'+hex_digest+'.png'):
                            screenpost='<a href="https://images.ransomware.live/screenshots/posts/' + hex_digest + '.png" target=_blank>📸</a>'
                    hash_object = hashlib.md5()
                    # Update the hash object with the string
                    hash_object.update(post['post_title'].replace('www.','').lower().encode('utf-8'))
                    # Get the hexadecimal representation of the hash
                    hex_digest = hash_object.hexdigest()
                    website = post.get('website', '').lower()
                    if os.path.exists('docs/domain/'+hex_digest+'.md'):
                        infostealer=' [🔎](domain/'+hex_digest+') '
                    elif website:
                        domain = extract_domain(website) #.replace('http://','').replace('https://','').replace('www.','')
                        hash_object = hashlib.md5()
                        hash_object.update(domain.encode('utf-8'))
                        hex_digest = hash_object.hexdigest()
                        if  os.path.exists('docs/domain/'+hex_digest+'.md'):
                            infostealer=' [🔎](domain/'+hex_digest+') '
                        else:
                            infostealer = ''
                    else:
                        infostealer = ''
                    description = clean_string(description)
                    if group['name'] == 'bianlian' or group['name'] == 'cloak':
                        line = '| ' + postURL + ' | ' + date + ' | ' + description + ' | ' + find_matching_victims(post['post_title'],group['name']) + '|' + screenpost + ' | ' + infostealer + ' |'
                    else:
                        line = '| ' + postURL + ' | ' + date + ' | ' + description + ' | ' + screenpost + ' |' + infostealer + ' |'
                        result = get_removal(post['post_title'], post['group_name'])
                        if result:  
                            line = '| *' + result +'* | ' + date + ' |   |   |   |'
                    writeline(profilepage, line)
        writeline(profilepage, '')
        #writeline(profilepage,' --- ')
        writeline(profilepage, '')
        groupcpt +=1
        stdlog('[' + str(groupcpt) + '/' + str(groupcount()) + '] Write ' + group['name'] + ' profile page')
        writeline(profilepage, '')
        writeline(profilepage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('profile pages generation complete')

def summaryjson():
    '''
    main markdown report generator - used with github pages
    '''
    stdlog('generating summary file')
    uptime_sheet = 'docs/datasummary.json'
    with open(uptime_sheet, 'w', encoding='utf-8') as f:
        f.close()
    writeline(uptime_sheet, '[')
    writeline(uptime_sheet, '{')
    writeline(uptime_sheet, '"groups": "' + str(groupcount()) + '",')
    writeline(uptime_sheet, '"servers": "' + str(hostcount()) + '",')
    writeline(uptime_sheet, '"online": "' + str(onlinecount()) + '",')
    writeline(uptime_sheet, '"postslast24": "' + str(postslast24h()) + '",')
    writeline(uptime_sheet, '"thismonthposts": "' + str(monthlypostcount()) + '",')
    writeline(uptime_sheet, '"currentmonth": "' + currentmonthstr() + '",')
    writeline(uptime_sheet, '"posts90days": "' + str(postssince(90)) + '",')
    writeline(uptime_sheet, '"poststhisyear": "' + str(postsyear(datetime.now().year)) + '",')
    writeline(uptime_sheet, '"currentyear": "' + str(datetime.now().year) + '",')
    writeline(uptime_sheet, '"overallposts": "' + str(postcount())   + '"')
    writeline(uptime_sheet, '}')
    writeline(uptime_sheet, ']')



def generate_admin_page(directory, output_file):
    # Ensure the directory exists
    if not os.path.exists(directory):
        print("Directory does not exist.")
        return

    # Get the list of files in the directory
    files = os.listdir(directory)
    
    # Filter image files (assuming common image file extensions)
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')
    image_files = [file for file in files if file.endswith(image_extensions)]

    # Create a dictionary to hold lists of files by topic
    images_by_topic = defaultdict(list)

    for file in image_files:
        # Split the file name to get the topic
        topic = file.split('-')[0]
        images_by_topic[topic].append(file)

    # Sort topics alphabetically
    sorted_topics = sorted(images_by_topic.keys())

    # Create the Markdown structure
    markdown_content = "# Administration\n"
    markdown_content += "> Restricted area \n"

    for topic in sorted_topics:
        images = images_by_topic[topic]
        topic_name = topic.replace("_", " ").capitalize().replace('.png','')
        markdown_content += "## {}\n".format(topic_name)
        markdown_content += "<table>\n"
        for i in range(0, len(images), 2):
            markdown_content += "  <tr>\n"
            markdown_content += "    <td><img src=\"/admin/{}\" alt=\"{}\" style=\"width:100%\"></td>\n".format(images[i], images[i])
            if i + 1 < len(images):
                markdown_content += "    <td><img src=\"/admin/{}\" alt=\"{}\" style=\"width:100%\"></td>\n".format(images[i + 1], images[i + 1])
            else:
                markdown_content += "    <td></td>\n"
            markdown_content += "  </tr>\n"
        markdown_content += "</table>\n"
        markdown_content += "\n"
    markdown_content += "## Statistics\n"
    markdown_content += "<a href='/admin/apistats.html' target=_blank>API</a> | <a href='/admin/webstats.html' target=_blank>web</a>\n" 


    # Write the Markdown content to a file
    with open(output_file, "w") as md_file:
        md_file.write(markdown_content)

def recentpublishedposts(top):
    '''
    create a list the last X posts (most recent)
    '''
    stdlog('finding recent posts')
    posts = openjson('./data/victims.json')
    # sort the posts by timestamp - descending
    sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
    # create a list of the last X posts
    recentposts = []
    for post in sorted_posts:
        recentposts.append(post)
        if len(recentposts) == top:
            break
    stdlog('recent posts generated')
    return recentposts

def recentpublishedpage():
    '''create a markdown table for the last 200 posts based on the published value'''
    fetching_count = 200
    stdlog('generating recent published victims page')
    recentpage = 'docs/recentvictims.md'
    # delete contents of file
    with open(recentpage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(recentpage,'# Recent victims')
    writeline(recentpage,'')
    writeline(recentpage, '> [!INFO] `Ransomware.live` provides tracking of ransomware groups and their victims. Descriptions available in the [group profiles view](profiles.md)')
    writeline(recentpage,'')
    writeline(recentpage, '**📰 200 last victims sorted by published date**')
    writeline(recentpage, '')
    writeline(recentpage, '| Attack Date | Victim | [Country](country) | Ransomware Group | 📸 |')
    writeline(recentpage, '|---|---|---|---|---|')
    for post in recentpublishedposts(fetching_count):
        # show friendly date for discovered
        date = post['published'].split(' ')[0]
        attacked_date = post.get('attacked_date', None)
        if attacked_date:
            date = attacked_date.split(' ')[0]
        # replace markdown tampering characters
        title = post['post_title'].replace('|', '-').replace('&amp;','&').replace('amp;','')
        group = post['group_name'].replace('|', '-')
        urlencodedtitle = urllib.parse.quote_plus(title)
        grouplink = '[' + group + '](group/' + group + ')'
        # screenpost='❌'
        screenpost=' '
        if post['post_url'] is not None: 
            # Create an MD5 hash object
            hash_object = hashlib.md5()
            # Update the hash object with the string
            hash_object.update(post['post_url'].encode('utf-8'))
            # Get the hexadecimal representation of the hash
            hex_digest = hash_object.hexdigest()
            if os.path.exists('docs/screenshots/posts/'+hex_digest+'.png'):
                screenpost='<a href="https://images.ransomware.live/screenshots/posts/' + hex_digest + '.png" target=_blank>👀</a>'
        if len(post['country']) > 1:
            flag = post['country']
            country="[!["+flag+"](https://images.ransomware.live/flags/"+flag+".svg ':size=32x24 :no-zoom')](country/"+flag.lower()+")"
        else:
            country=''
        line = '| ' + date + ' | [`' + title + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + country + ' | ' + grouplink + ' | ' + screenpost + ' |'
        result = get_removal(title, group)
        if result:  
             line = '| ' + date + ' |  *' + result + '* | ' + country + ' | ' + grouplink + ' |   |   |'
        writeline(recentpage, line)
    writeline(recentpage, '')
    writeline(recentpage, '> [!TIP] You can also check the 200 last victims sorted by discovered date by `Ransomware.live` [here](recentdiscoveredvictims.md).')
    writeline(recentpage, '')
    writeline(recentpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('recent published victims page generated')


#### 
# Need for generate_country_reports
###

def format_date(date_string):
    try:
        date_string=date_string.replace('T',' ')
        date_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        errlog('Error generating country page : '+date_string)

def count_post_titles_by_country(country_code):
    with open('./data/victims.json', 'r') as file:
        posts_data = json.load(file)    
    count = 0
    for post in posts_data:
        if post.get('country') == country_code:
            count += 1
    return count

def get_removal(victim, group, json_file='./data/removerequests.json'):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    if victim == data.get("victim_name") and group == data.get("group_name"):
        applicant = data.get("applicant")
        #return f"Removed at the request of {applicant}"
        return applicant
    return None

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
                result = get_removal(victim['name'], victim['group_name'])
                if result:  
                    country_file.write(f"|{victim['discovered_date']}|{victim['published_date']}| *{result}* | [{victim['group_name']}](group/{victim['group_name']})| | |\n")
                else:
                    country_file.write(f"|{victim['discovered_date']}|{victim['published_date']}|[{victim['name'].replace('|','-')}](https://google.com/search?q={victim['name'].replace('|','-').replace(' ','+')})|[{victim['group_name']}](group/{victim['group_name']})| {screenpost}| {infostealer} |\n")
                counter += 1 
            country_file.write(f"\n\n{counter} victims found\n\n")
            country_file.write('Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')

def get_cert_info_by_country(country_code):
    cert_info = []
    # Load the JSON data from the file
    with open('./data/eucert.json') as json_file:
        cert = json.load(json_file)
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


def generate_country_reports():
    # Read the JSON file
    with open('./data/victims.json', 'r') as file:
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

    # Load posts from JSON file
    with open('./data/victims.json', 'r') as file:
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
        #stdlog('Create page for ' + country_code)
        create_country_victims_file(country_code, victims_data,html_content)

def ttps():
    with open('./data/groups.json', 'r') as json_file:
        groups_data = json.load(json_file)

    # Check each group for a StopRansomware report and replace the profile if found
    for group in groups_data:
        update = False
        original_group_name = group['name']
        group_name = group['name'].lower()

        if group_name == 'lockbit':
            group_name = 'lockbit_old'
        elif group_name == 'lockbit3':
            group_name = 'lockbit'

        with open('template_ttps.md', 'r') as file:
            template_content = file.read()
        
        new_content = template_content
        
        for file_tools in ['CredentialTheft', 'DefenseEvasion', 'DiscoveryEnum', 'Exfiltration', 'LOLBAS', 'Networking', 'Offsec', 'RMM-Tools']:
            tools = get_tools_by_group(group_name, f'./import/Ransomware-Tool-Matrix/Tools/{file_tools}.md')
            
            if tools:
                tools_list = ''
                for tool in tools:   
                    tools_list += '* ' + tool + '\n'  # Accumulate the tool list correctly
                new_content = new_content.replace('{{' + file_tools + '}}', tools_list)
                update = True 
            else:
                new_content = new_content.replace('{{' + file_tools + '}}', 'N/A')


        if update:
            #directory_path = '/var/www/ransomware-ng/import/Ransomware-Tool-Matrix/GroupProfiles/'
            #files_in_directory = os.listdir(directory_path)
            #filename = f'{group_name}.md' 
            #for file in files_in_directory:
            #    if file.lower() == filename.lower():
            #        line = f"[filename](https://raw.githubusercontent.com/BushidoUK/Ransomware-Tool-Matrix/main/GroupProfiles/{file} ':include')"
            #        print(line)
            #    else: 
            #        line =''
            #new_content = new_content.replace('{{EXTRA}}', line)
            
            new_content = new_content.replace('{{GROUPE_NAME}}', original_group_name)
            with open(f'./docs/ttps/{original_group_name}.md', 'w') as new_file:
                new_file.write(new_content)

        

