#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
collection of shared modules used throughout ransomwatch
'''
import os
import sys
import json
import socket
# import codecs
import random
import calendar
import tweepy
import logging
from datetime import datetime
from datetime import timedelta
import subprocess
import tldextract
import lxml.html
import requests
import pandas as pd
from dotenv import load_dotenv
import http.client, urllib
from mastodon import Mastodon
import hashlib

sockshost = '127.0.0.1'
socksport = 9050

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO
    )

def stdlog(msg):
    '''standard infologging'''
    logging.info(msg)

def dbglog(msg):
    '''standard debug logging'''
    logging.debug(msg)

def errlog(msg):
    '''standard error logging'''
    logging.error(msg)

def honk(msg):
    '''critical error logging with termination'''
    logging.critical(msg)
    sys.exit()

def currentmonthstr():
    '''
    return the current, full month name in lowercase
    '''
    return datetime.now().strftime('%B').lower()

# socks5h:// ensures we route dns requests through the socks proxy
# reduces the risk of dns leaks & allows us to resolve hidden services

oproxies = {
    'http':  'socks5h://' + str(sockshost) + ':' + str(socksport),
    'https': 'socks5h://' + str(sockshost) + ':' + str(socksport)
}


def randomagent():
    '''
    randomly return a useragent from assets/useragents.txt
    '''
    with open('assets/useragents.txt', encoding='utf-8') as uafile:
        uas = uafile.read().splitlines()
        uagt = random.choice(uas)
        dbglog('sharedutils: ' + 'random user agent - ' + str(uagt))
    return uagt

def headers():
    '''
    returns a key:val user agent header for use with the requests library
    '''
    headerstr = {'User-Agent': str(randomagent())}
    return headerstr

def metafetch(url):
    '''
    return the status code & http server using oproxies and headers
    '''
    try:
        stdlog('sharedutils: ' + 'meta prefetch request to ' + str(url))
        request = requests.head(url, proxies=oproxies, headers=headers(), timeout=20)
        statcode = request.status_code
        try:
            response = request.headers['server']
            return statcode, response
        except KeyError as ke:
            errlog('sharedutils: ' + 'meta prefetch did not discover server - ' + str(ke))
            return statcode, None
    except requests.exceptions.Timeout as ret:
        errlog('sharedutils: ' + 'meta request timeout - ' + str(ret))
        return None, None
    except requests.exceptions.ConnectionError as rec:
        errlog('sharedutils: ' + 'meta request connection error - ' + str(rec))
        return None, None

def socksfetcher(url):
    '''
    fetch a url via socks proxy
    '''
    try:
        stdlog('sharedutils: ' + 'starting socks request to ' + str(url))
        request = requests.get(url, proxies=oproxies, headers=headers(), timeout=20, verify=False)
        dbglog(
            'sharedutils: ' + 'socks request - recieved statuscode - ' \
                + str(request.status_code)
            )
        try:
            response = request.text
            return response
        except AttributeError as ae:
            errlog('sharedutils: ' + 'socks response error - ' + str(ae))
            return None
    except requests.exceptions.Timeout:
        errlog('geckodriver: ' + 'socks request timed out!')
        return None
    except requests.exceptions.ConnectionError as rec:
        # catch SOCKSHTTPConnectionPool Host unreachable
        if 'SOCKSHTTPConnectionPool' and 'Host unreachable' in str(rec):
            errlog('sharedutils: ' + 'socks request unable to route to host, check hsdir resolution status!')
            return None
        errlog('sharedutils: ' + 'socks request connection error - ' + str(rec))
        return None

def siteschema(location):
    '''
    returns a dict with the site schema
    '''
    if not location.startswith('http'):
        dbglog('sharedutils: ' + 'assuming we have been given an fqdn and appending protocol')
        location = 'http://' + location
    schema = {
        'fqdn': getapex(location),
        'title': None,
        'version': getonionversion(location)[0],
        'slug': location,
        'available': False,
        'delay': None,
        'updated': None,
        'lastscrape': '2021-05-01 00:00:00.000000',
        'enabled': True
    }
    dbglog('sharedutils: ' + 'schema - ' + str(schema))
    return schema

def runshellcmd(cmd):
    '''
    runs a shell command and returns the output
    '''
    stdlog('sharedutils: ' + 'running shell command - ' + str(cmd))
    cmdout = subprocess.run(
        cmd,
        shell=True,
        universal_newlines=True,
        check=True,
        stdout=subprocess.PIPE
        )
    response = cmdout.stdout.strip().split('\n')
    # if empty list output, error
    # if len(response) == 1:
    #     honk('sharedutils: ' + 'shell command returned no output')
    return response

def getsitetitle(html) -> str:
    '''
    tried to parse out the title of a site from the html
    '''
    stdlog('sharedutils: ' + 'getting site title')
    try:
        title = lxml.html.parse(html)
        titletext = title.find(".//title").text
    except AssertionError:
        stdlog('sharedutils: ' + 'could not fetch site title from source - ' + str(html))
        return None
    except AttributeError:
        stdlog('sharedutils: ' + 'could not fetch site title from source - ' + str(html))
        return None
    # limit title text to 50 chars
    if titletext is not None:
        if len(titletext) > 50:
            titletext = titletext[:50]
        stdlog('sharedutils: ' + 'site title - ' + str(titletext))
        return titletext
    stdlog('sharedutils: ' + 'could not find site title from source - ' + str(html))
    return None

def gcount(posts):
    group_counts = {}
    for post in posts:
        if post['group_name'] in group_counts:
            group_counts[post['group_name']] += 1
        else:
            group_counts[post['group_name']] = 1
    return group_counts

def gcountYear(posts,year):
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    date_debut = datetime(year, 1, 1)
    date_fin = datetime(year, 12, 31)
    group_counts = {}
    for post in posts:
        if post['group_name'] in group_counts:
            date = datetime.strptime(post['discovered'], date_format)
            if date <= date_fin and date >= date_debut:
                group_counts[post['group_name']] += 1
        else:
            date = datetime.strptime(post['discovered'], date_format)
            if date <= date_fin and date >= date_debut:
                group_counts[post['group_name']] = 1
    return group_counts


def last_day_of_month(month, year):
    # Obtenir le dernier jour du mois en utilisant la fonction monthrange de la bibliothèque calendar
    last_day = calendar.monthrange(year, month)[1]
    return last_day

def gcountMonth(posts,year,month=0):
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    if month == 0:
        date_debut = datetime(year, 1, 1)
        date_fin = datetime(year, 12, 31)
    else: 
        date_debut = datetime(year, month, 1)
        date_fin = datetime(year, month, last_day_of_month(month,year))
    group_counts = {}
    for post in posts:
        if post['group_name'] in group_counts:
            date = datetime.strptime(post['published'], date_format)
            if date <= date_fin and date >= date_debut:
                group_counts[post['group_name']] += 1
        else:
            date = datetime.strptime(post['published'], date_format)
            if date <= date_fin and date >= date_debut:
                group_counts[post['group_name']] = 1
    return group_counts


def hasprotocol(slug):
    '''
    checks if a url begins with http - cheap protocol check before we attampt to fetch a page
    '''
    return bool(slug.startswith('http'))

def getapex(slug):
    '''
    returns the domain for a given webpage/url slug
    '''
    stripurl = tldextract.extract(slug)
    print(stripurl)
    if stripurl.subdomain:
        return stripurl.subdomain + '.' + stripurl.domain + '.' + stripurl.suffix
    return stripurl.domain + '.' + stripurl.suffix

def striptld(slug):
    '''
    strips the tld from a url
    '''
    stripurl = tldextract.extract(slug)
    return stripurl.domain

def getonionversion(slug):
    '''
    returns the version of an onion service (v2/v3)
    https://support.torproject.org/onionservices/v2-deprecation
    '''
    version = None
    stripurl = tldextract.extract(slug)
    location = stripurl.domain + '.' + stripurl.suffix
    stdlog('sharedutils: ' + 'checking for onion version - ' + str(location))
    if len(stripurl.domain) == 16:
        stdlog('sharedutils: ' + 'v2 onionsite detected')
        version = 2
    elif len(stripurl.domain) == 56:
        stdlog('sharedutils: ' + 'v3 onionsite detected')
        version = 3
    else:
        stdlog('sharedutils: ' + 'unknown onion version, assuming clearnet')
        version = 0
    return version, location

def openhtml(file):
    '''
    opens a file and returns the html
    '''
    with open(file, 'r', encoding='utf-8') as f:
        html = f.read()
    return html

def openjson(file):
    '''
    opens a file and returns the json as a dict
    '''
    with open(file, encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    return data

def checktcp(host, port):
    '''
    checks if a tcp port is open - used to check if a socks proxy is available
    '''
    stdlog('sharedutils: ' + 'attempting socket connection')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((str(host), int(port)))
    sock.close()
    if result == 0:
        stdlog('sharedutils: ' + 'socket - successful connection')
        return True
    stdlog('sharedutils: ' + 'socket - failed connection')
    return False

def postcount():
    post_count = 1
    posts = openjson('posts.json')
    for post in posts:
        post_count += 1
    return post_count

def grouppostavailable(groupname):
    grouppost_count = 0
    posts = openjson('posts.json')
    for post in posts:
        if post['group_name'] == groupname:
            grouppost_count += 1
    if grouppost_count > 0:
        return True
    else:
        return False

def grouppostcount(groupname):
    grouppost_count = 0
    posts = openjson('posts.json')
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

def postcountgroup(groupname):
    grouppost_count = 0
    posts = openjson('posts.json')
    for post in posts:
        if post['group_name'] == groupname:
            grouppost_count += 1
    return grouppost_count

def groupcount():
    groups = openjson('groups.json')
    return len(groups)

def parsercount():
    groups = openjson('groups.json')
    parse_count = 1
    for group in groups:
        if group['parser'] is True:
            parse_count += 1
    return parse_count

def hostcount():
    groups = openjson('groups.json')
    host_count = 0
    for group in groups:
        for host in group['locations']:
            host_count += 1
    return host_count

def headlesscount():
    groups = openjson('groups.json')
    js_count = 0
    for group in groups:
        if group['javascript_render'] is True:
            js_count += 1
    return js_count

def onlinecount():
    groups = openjson('groups.json')
    online_count = 0
    for group in groups:
        for host in group['locations']:
            if host['available'] is True:
                online_count += 1
    return online_count

def version2count():
    groups = openjson('groups.json')
    version2_count = 0
    for group in groups:
        for host in group['locations']:
            if host['version'] == 2:
                version2_count += 1
    return version2_count

def version3count():
    groups = openjson('groups.json')
    version3_count = 0
    for group in groups:
        for host in group['locations']:
            if host['version'] == 3:
                version3_count += 1
    return version3_count

def monthlypostcount():
    '''
    returns the number of posts within the current month
    '''
    post_count = 0
    posts = openjson('posts.json')
    current_month = datetime.now().month
    current_year = datetime.now().year
    for post in posts:
        datetime_object = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime_object.year == current_year and datetime_object.month == current_month:
            post_count += 1
    return post_count

def postssince(days):
    '''returns the number of posts within the last x days'''
    post_count = 0
    posts = openjson('posts.json')
    for post in posts:
        datetime_object = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime_object > datetime.now() - timedelta(days=days):
            post_count += 1
    return post_count

def poststhisyear():
    '''returns the number of posts within the current year'''
    post_count = 0
    posts = openjson('posts.json')
    current_year = datetime.now().year
    for post in posts:
        datetime_object = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime_object.year == current_year:
            post_count += 1
    return post_count

def postslastyear():
    '''
    returns the number of posts last year
    '''
    post_count = 0
    posts = openjson('posts.json')
    previous_year = datetime.now() - timedelta(days=365)
    previous_year = previous_year.year 
    for post in posts:
        datetime_object = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime_object.year == previous_year:
            post_count += 1
    return post_count

def postslast24h():
    '''returns the number of posts within the last 24 hours'''
    post_count = 0
    posts = openjson('posts.json')
    for post in posts:
        datetime_object = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime_object > datetime.now() - timedelta(hours=24):
            post_count += 1
    return post_count

def countcaptchahosts():
    '''returns a count on the number of groups that have captchas'''
    groups = openjson('groups.json')
    captcha_count = 0
    for group in groups:
        if group['captcha'] is True:
            captcha_count += 1
    return captcha_count

def postsjson2cvs():
    df = pd.read_json (r'posts.json')
    df.to_csv (r'docs/posts.csv', index = None) 


def countpostsyeartodate():
    posts = openjson('posts.json')
    # Obtenir l'année courante et soustraire 1 pour obtenir l'année précédente
    current_year = datetime.now().year
    year_last_year = current_year - 1
    # Convertir la date actuelle de l'année précédente au format datetime
    date_last_year = datetime.now().replace(year=year_last_year)
    # Compter les publications qui tombent dans la plage de dates
    count_posts_last_year = 0
    for post in posts:
        published_date = datetime.strptime(post["published"], "%Y-%m-%d %H:%M:%S.%f")
        if datetime(year_last_year, 1, 1) <= published_date <= date_last_year:
            count_posts_last_year += 1
    return count_posts_last_year



def totwitter(post_title, group):
    dbglog('sharedutils: ' + 'posting to twitter')
    try:
        client = tweepy.Client(
            consumer_key=os.environ.get('TWITTER_CONSUMER_KEY'),
            consumer_secret=os.environ.get('TWITTER_CONSUMER_SECRET'),
            access_token=os.environ.get('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
            )
        status = str(group) + ' : ' + str(post_title) + ' https://www.ransomware.live/#/profiles?id=' + str(group)
        client.create_tweet(text=status)
    except TypeError as te:
        honk('sharedutils: ' + 'twitter tweepy unsatisfied: ' + str(te))

def todiscord(post_title, group, webhook):
    '''
    sends a post to a discord webhook defined as an envar
    '''
    dbglog('sharedutils: ' + 'sending to discord webhook')
    # avoid json decode errors by escaping the title if contains \ or "
    post_title = post_title.replace('\\', '\\\\').replace('"', '\\"')
    discord_data = '''
    {
    "content": "`%s`",
    "embeds": [
        {
        "color": null,
        "author": {
            "name": "%s",
            "url": "https://www.ransomware.live/#/profiles?id=%s",
            "icon_url": "https://avatars.githubusercontent.com/u/10137"
        }
        }
    ]
    }''' % (post_title, group, group)
    discord_json = json.loads(discord_data)
    stdlog('sharedutils: ' + 'sending to discord webhook')
    dscheaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    try:
        hook_uri = webhook
        hookpost = requests.post(hook_uri, json=discord_json, headers=dscheaders)
    except requests.exceptions.RequestException as e:
        honk('sharedutils: ' + 'error sending to discord webhook: ' + str(e))
    if hookpost.status_code == 204:
        return True
    if hookpost.status_code == 429:
        errlog('sharedutils: ' + 'discord webhook rate limit exceeded')
    else:
        honk('sharedutils: ' + 'recieved discord webhook error resonse ' + str(hookpost.status_code) + ' with text ' + str(hookpost.text))
    return False


def toMastodon(post_title, group_name): 
    '''
    send a post to Mastodon 
    '''
    load_dotenv()
    mastodon = Mastodon(
    access_token =  os.getenv('MASTODON_TOKEN'),
    api_base_url = 'https://infosec.exchange/'
    )
    mastodon.status_post("🏴‍☠️ A new victim called "+ post_title + " has been claimed by #Ransomware group "+ group_name+'. More information at https://ransomware.live')

def toPushover(post_title, group_name):
    stdlog('Send notification')
    load_dotenv()
    USER_KEY=os.getenv('PUSH_USER')
    API_KEY= os.getenv('PUSH_API')
    MESSAGE = "<b>" + post_title +  "</b> est victime du ransomware <b>" + group_name + "</b>"
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
              "token": API_KEY,
              "user": USER_KEY,
              "message": MESSAGE,
              "html": 1
            }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()


def toteams(post_title, group):
    '''
    sends a post to a miCroSoFt tEaMs webhook defined as an envar
    '''
    dbglog('sharedutils: ' + 'sending to microsoft teams webhook')
    # avoid json decode errors by escaping the title if contains \ or "
    post_title = post_title.replace('\\', '\\\\').replace('"', '\\"')
    teams_data = '''
    {
    "type":"message",
    "attachments":[
        {
            "contentType":"application/vnd.microsoft.card.adaptive",
            "contentUrl":null,
            "content":{
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "%s",
                        "isSubtle": true,
                        "wrap": true
                    }
                ],
                "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "%s",
                        "url": "https://www.ransomware.live/#/profiles?id=%s"
                    }
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.4"
            }
        }
    ]
    }''' % (post_title, group, group)
    try:
        hook_uri = os.environ.get('MS_TEAMS_WEBHOOK')
        hookpost = requests.post(hook_uri, data=teams_data, headers={'Content-Type': 'application/json'})
    except requests.exceptions.RequestException as e:
        honk('sharedutils: ' + 'error sending to microsoft teams webhook: ' + str(e))
    if hookpost.status_code == 200:
        return True
    if hookpost.status_code == 429:
        errlog('sharedutils: ' + 'microsoft teams webhook rate limit exceeded')
    else:
        honk('sharedutils: ' + 'recieved microsoft teams webhook error resonse ' + str(hookpost.status_code) + ' with text ' + str(hookpost.text))
    return False
    
def find_slug_by_md5(group_name, target_md5):
    # Load the JSON data from the file or source
    data = openjson('groups.json')
    
    # Find the group entry in the data
    group_entry = next((group for group in data if group['name'] == group_name), None)

    if group_entry:
        # Extract the slugs from the locations
        slugs = [location['slug'] for location in group_entry['locations']]
        
        # Calculate the MD5 hash for each slug and compare with the target MD5
        for slug in slugs:
            md5 = hashlib.md5(slug.encode()).hexdigest()
            if md5 == target_md5:
                return slug
    else:
        return None

def extract_md5_from_filename(file_name):
    parts = file_name.rsplit("-", 1)
    
    if len(parts) == 2:
        before_hyphen, after_hyphen = parts
        dot_position = after_hyphen.rfind(".")
        
        if dot_position != -1:
            extracted_text = after_hyphen[:dot_position]
            return extracted_text