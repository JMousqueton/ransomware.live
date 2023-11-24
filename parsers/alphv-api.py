import requests
import socks
import json
from sharedutils import stdlog, dbglog, errlog   # , honk
from sharedutils import openjson
import datetime
from parse import appender


# Assuming Tor is running on default port 9050.
proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

def existingpost(post_title, group_name):
    '''
    check if a post already exists in posts.json
    '''
    posts = openjson('posts.json')
    # posts = openjson('posts.json')
    for post in posts:
        if post['post_title'].lower() == post_title.lower() and post['group_name'] == group_name:
            return True
    return False

def fetch_json_from_onion_url(onion_url):
    try:
        response = requests.get(onion_url, proxies=proxies,verify=False)
        response.raise_for_status()  # Check for any HTTP errors
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

    # Assuming the response contains JSON data, parse it
    json_data = response.json()
    return json_data

def convert_date(timestamp):
    # Convert the timestamp to a datetime object
    date_object = datetime.datetime.fromtimestamp(timestamp /  1000)
    # Format the date as per your desired output format, including microseconds
    formatted_date = date_object.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_date

def main():
    onion_url= 'http://alphvmmm27o3abo3r2mlmjrpdmzle3rykajqc5xsj7j7ejksbpsa36ad.onion/api/blog/brief/0/10'

    json_data = fetch_json_from_onion_url(onion_url)
    if json_data is not None:
        i=0
        for item in json_data['items']:
            id = item['id']
            post_title = item['title'].strip().rstrip('.')
            if existingpost(post_title, 'alphv') is False:
                desc_url = 'http://alphvmmm27o3abo3r2mlmjrpdmzle3rykajqc5xsj7j7ejksbpsa36ad.onion/api/blog/' + id
                json_data_item = fetch_json_from_onion_url(desc_url)
                if json_data_item is not None:
                        created_dt = json_data_item.get('createdDt')
                        title = json_data_item.get('title').strip()
                        try: # Extract the required fields
                            url = json_data_item.get('publication', {}).get('url')
                        except:
                            url = ''
                        try:
                            description = json_data_item.get('publication', {}).get('description')
                        except:
                            description = ''
                        """
                        +------------------------------+------------------+----------+
                        | Description | Published Date | Victim's Website | Post URL |
                        +------------------------------+------------------+----------+
                        |      X      |      X         |                 |     x    |
                        +------------------------------+------------------+----------+
                        Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
                        """
                        appender(title.rstrip('.'), 'alphv', description.replace('\n',' '),url,convert_date(created_dt)+'.123456','http://alphvmmm27o3abo3r2mlmjrpdmzle3rykajqc5xsj7j7ejksbpsa36ad.onion/' + id)
