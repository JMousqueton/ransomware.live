#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
parses the source html for each group where a parser exists & contributed to the post dictionary
always remember..... https://stackoverflow.com/questions/1732348/regex-match-open-tags-except-xhtml-self-contained-tags/1732454#1732454
'''
import os, hashlib
import json,re, html, time, requests, random
from sys import platform
from datetime import datetime
from bs4 import BeautifulSoup # type: ignore
from sharedutils import openjson
from sharedutils import runshellcmd
# from sharedutils import todiscord, totwitter, toteams
from sharedutils import toMastodon, toPushover, tobluesky, tomattermost
from sharedutils import stdlog, dbglog, errlog   # , honk
# For screenshot 
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
# For watermark on screenshot 
from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL.PngImagePlugin import PngInfo
from datetime import datetime
# For Notification 
import http.client, urllib
from dotenv import load_dotenv

# on macOS we use 'grep -oE' over 'grep -oP'
if platform == 'darwin':
    fancygrep = 'ggrep -oP'
else:
    fancygrep = 'grep -oP'


def add_watermark(image_path, watermark_image_path='./docs/ransomwarelive.png'):
    """
    Adds a watermark image (with 50% transparency) to the center of the input image and overwrites it.
    
    :param image_path: Path to the image to be watermarked.
    :param watermark_image_path: Path to the watermark image.
    :return: None
    """
    Image.MAX_IMAGE_PIXELS = None
    # Open the image to be watermarked
    stdlog('open image ' + image_path)
    original = Image.open(image_path)
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
    
    # Open the watermark image
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
    stdlog('save watermaked image ' + image_path)
    original.save(image_path, 'PNG')

def posttemplate(victim, group_name, timestamp,description,website,published,post_url,country):
    '''
    assuming we have a new post - form the template we will use for the new entry in posts.json
    '''
    schema = {
        'post_title': victim,
        'group_name': group_name,
        'discovered': timestamp,
        'description': description,
        'website': website,
        'published' : published,
        'post_url' : post_url,
        'country'   : country
    }
    dbglog(schema)
    return schema

def screenshot(webpage,fqdn,delay=15000,output=None):
    stdlog('webshot: {}'.format(webpage))
    if output is None:
        name = 'docs/screenshots/' + fqdn.replace('.', '-') + '.png'
        stdlog("Mode : blog")
    else: 
        stdlog('Post Screenshot --> ' + output)
        name = 'docs/screenshots/posts/' + output + '.png'
        stdlog("Mode : post")
    #try:
        with sync_playwright() as play:
                try:
                    tor_prefixes = ["http://stniiomy", "http://noescape", "http://medusa", "http://cactus", "http://hl666"]
                    if any(webpage.startswith(prefix) for prefix in tor_prefixes):
                        browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                            args=[''])
                            #args=['--unsafely-treat-insecure-origin-as-secure='+host['slug']])
                        stdlog('(!) exception')
                    elif webpage.startswith("https://ransomed.vc/"):
                        browser = play.firefox.launch()
                        stdlog('(!) not via tor')
                    elif webpage.startswith("https://t.me/"):
                        browser = play.firefox.launch()
                        stdlog('(!) not via tor')
                    elif webpage.startswith("http://knight"):
                        browser = play.chromium.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                            args=["--headless=new"])
                        stdlog('(!) exception')
                    else:
                        browser = play.chromium.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                            args=[''])
                            #args=['--unsafely-treat-insecure-origin-as-secure='+host['slug']])
                    context = browser.new_context(ignore_https_errors= True )
                    Image.MAX_IMAGE_PIXELS = None
                    page = context.new_page()
                    page.goto(webpage, wait_until='load', timeout = 120000)
                    page.bring_to_front()
                    page.wait_for_timeout(delay)
                    page.mouse.move(x=500, y=400)
                    page.wait_for_load_state('networkidle')
                    page.mouse.wheel(delta_y=2000, delta_x=0)
                    page.wait_for_load_state('networkidle')
                    page.wait_for_timeout(5000)
                    page.screenshot(path=name, full_page=True)
                    image = Image.open(name)
                    metadata = PngInfo()
                    metadata.add_text("Source", "Ransomware.live")
                    metadata.add_text("Copyright", "Ransomware.live")
                    metadata.add_text("Description",webpage)
                    metadata.add_text("Author","Julien Mousqueton")
                    
                    # Get current date and time
                    current_datetime = datetime.now()
                    # Format it in ISO format
                    iso_formatted = current_datetime.isoformat()
                    current_date = current_datetime.strftime('%Y:%m:%d %H:%M:%S')
                    
                    metadata.add_text("Creation Time",current_date)
                    
                    draw = ImageDraw.Draw(image)
                    draw.text((10, 10), iso_formatted, fill=(0, 0, 0))
                    #draw.text((10, 10), "https://www.ransomware.live", fill=(0, 0, 0))
                    
                    image.save(name, pnginfo=metadata)
                    add_watermark(name)
                except PlaywrightTimeoutError:
                    stdlog('Timeout!')
                except Exception as exception:
                    errlog(exception)
                browser.close()

    #except:
    #         stdlog('Impossible to webshot {}'.format(webpage))


def existingpost(post_title, group_name):
    '''
    check if a post already exists in posts.json
    '''
    posts = openjson('posts.json')
    # posts = openjson('posts.json')
    for post in posts:
        if post['post_title'].lower() == post_title.lower() and post['group_name'] == group_name:
            #dbglog('post already exists: ' + post_title)
            return True
    dbglog('post does not exist: ' + post_title)
    return False

def gettitlefromURL(website_url):
    if not website_url.startswith("www"):
                website_url = "www." + website_url
    # check if the post_title starts with "http" or "https"
    if not website_url.startswith("http"):
        website_url = "https://" + website_url
    # retrieve the title of the website from its URL
    try:
        with open("assets/useragents.txt", "r") as f:
            user_agents = f.readlines()
        # Strip newlines from the user agents
        user_agents = [ua.strip() for ua in user_agents]
        # Pick a random user agent
        headers = {'User-Agent': random.choice(user_agents)}
        # Make the request
        page = requests.get(website_url, headers=headers, timeout=10)
        # page = requests.get(website_url,timeout=10)
        soup = BeautifulSoup(page.content, 'html.parser')
        website_title = soup.find('title').get_text()
        website_title = re.sub(r'[\r\n\t]', '', website_title).replace('|', '-')
        # add the title of the website as the description
        description = website_title
    except requests.exceptions.Timeout:
        stdlog('Website did not respond, timeout')
        description = ""
    except:
        stdlog('Website did not respond')
        description = ""
    return description

def replace_http_slash(text):
    # Use regular expression to replace http:/
    text = re.sub(r'http:/([^/])', r'http://\1', text)
    # Use regular expression to replace https:/
    text = re.sub(r'https:/([^/])', r'https://\1', text)
    return text


def appender(post_title, group_name, description="", website="", published="", post_url="", country=""):
    '''
    append a new post to posts.json
    '''
    if len(post_title) == 0:
        stdlog('post_title is empty')
        return
    # Check exclusion 
    with open('exceptions.txt', 'r') as f:
    # Read the contents of the file
        exceptions = f.read()
        if post_title in exceptions:
            stdlog('(!) '+ post_title + ' is in exceptions')
            return
    # limit length of post_title to 90 chars
    #country=''
    if len(post_title) > 90:
        post_title = post_title[:90]
    post_title=html.unescape(post_title)
    if existingpost(post_title, group_name) is False:
        print('==> ' + post_title)
        posts = openjson('posts.json')
        if description == "_URL_":
            description = gettitlefromURL(post_title)
            print(post_title)
            # if not post_title.lower.startswith("www"):
            website =  "www." + post_title
            website = "https://" + website
        if published == "":
            published = str(datetime.today())
        newpost = posttemplate(post_title, group_name, str(datetime.today()),description,replace_http_slash(website),published,post_url,country)
        stdlog('adding new post - ' + 'group:' + group_name + ' title:' + post_title)
        posts.append(newpost)
        with open('posts.json', 'w', encoding='utf-8') as outfile:
            '''
            use ensure_ascii to mandate utf-8 in the case the post contains cyrillic 🇷🇺
            https://pynative.com/python-json-encode-unicode-and-non-ascii-characters-as-is/
            '''
            dbglog('writing changes to posts.json')
            json.dump(posts, outfile, indent=4, ensure_ascii=False)
        load_dotenv()
        # if socials are set try post
        #if os.environ.get('DISCORD_WEBHOOK_1') is not None:
        #    todiscord(newpost['post_title'], newpost['group_name'], os.environ.get('DISCORD_WEBHOOK_1'))
        #if os.environ.get('DISCORD_WEBHOOK_2') is not None:
        #    todiscord(newpost['post_title'], newpost['group_name'], os.environ.get('DISCORD_WEBHOOK_2'))
        #if os.environ.get('TWITTER_ACCESS_TOKEN') is not None:
        #    totwitter(newpost['post_title'], newpost['group_name'])
        #if os.environ.get('MS_TEAMS_WEBHOOK') is not None:
        #    toteams(newpost['post_title'], newpost['group_name'])
        # Mastodon notification 
        if os.environ.get('MASTODON_TOKEN') is not None:
 #           toMastodon(post_title,group_name)
            print("")

        # Pushover notification 
        if os.environ.get('PUSH_API') is not None:
            toPushover(post_title, group_name)
        
        if os.environ.get('BLUESKY_APP_PASSWORD') is not None:
            tobluesky(post_title, group_name)
            tomattermost(post_title, group_name)
        
        ### Post screenshot
        if post_url !="":
            hash_object = hashlib.md5()
            hash_object.update(post_url.encode('utf-8'))
            hex_digest = hash_object.hexdigest()
            screenshot(post_url,None,15000,hex_digest)
        ### Screenshot blog
        #groups = openjson('groups.json')
        #for group in groups:
        #    if group["name"] == group_name:
        #        for webpage in group['locations']:
        #            delay = webpage['delay']*1000 if ( 'delay' in webpage and webpage['delay'] is not None ) \
        #                else 15000
        #            screenshot('http://'+webpage['fqdn'],webpage['fqdn'],delay)
    #else:
    #    stdlog(post_title + ' already exists')
