import json 
import logging
from datetime import datetime as dt
from dotenv import load_dotenv
import os,hashlib
from urllib.parse import urlparse
import requests
# For screenshot 
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
# For watermark on screenshot 
from PIL import Image
from PIL import ImageDraw

load_dotenv()

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO
    )

NowTime=dt.now()

def screenshot(webpage,output,delay=15000,option=None):
    stdlog('webshot: {}'.format(webpage))
    name = 'docs/screenshots/press/' + output + '.png'
    with sync_playwright() as play:
                try:
                    browser = play.chromium.launch()
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
                    draw = ImageDraw.Draw(image)
                    draw.text((10, 10), "https://www.ransomware.live", fill=(0, 0, 0))
                    image.save(name)
                except PlaywrightTimeoutError:
                    stdlog('Timeout!')
                except Exception as exception:
                    errlog(exception)
                    errlog("error")
                #browser.close()



def openjson(url):
    '''
    opens a file and returns the json as a dict
    '''
    response = requests.get(url)
    data = json.loads(response.text)
    return data

def stdlog(msg):
    '''standard infologging'''
    logging.info(msg)

def dbglog(msg):
    '''standard debug logging'''
    logging.debug(msg)

def errlog(msg):
    '''standard error logging'''
    logging.error(msg)

def writeline(file, line):
    '''write line to file'''
    with open(file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
        f.close()

def press(top):
    '''
    create a list the last X posts (most recent)
    '''
    stdlog('finding recent tweets')
    attacks = openjson('https://data.ransomware.live/press.json')
    # sort the posts by timestamp - descending
    sorted_attacks = sorted(attacks, key=lambda x: x['date'], reverse=True)
    # create a list of the last X posts
    recentnews = []
    for attack in sorted_attacks:
        recentnews.append(attack)
        if len(recentnews) == top:
            break
    stdlog('recent news generated')
    return recentnews


def pressmarkdown():
    stdlog('Generating news markdown')
    tweetspage = 'docs/press.md'
    fetching_count = 333
    # delete contents of file
    with open(tweetspage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(tweetspage,'')
    writeline(tweetspage, '# 🗞️ Ransomware.live in the press')
    writeline(tweetspage,'\n')
    writeline(tweetspage, '> [!TIP]')
    writeline(tweetspage, '> `Ransomware.live` is mentionned in the press, find bellow the recent articles found.')
    writeline(tweetspage,'')
    writeline(tweetspage, '\n')
    writeline(tweetspage, '| Date | Source | Title | Screenshot | ')
    writeline(tweetspage, '|---|---|---|---|')
    compteur = 0  # Initialisation du compteur à 0
    for tweet in press(fetching_count):
        news_date = tweet['date']
        news_victim = tweet['source'] 
        news_country = tweet['title'] 
        news_url = tweet['url']  
        parsed_url = urlparse(news_url)
    
        # Calculate the MD5 checksum of the "post_url" value
        news_url_bytes = news_url.encode('utf-8')
        news_md5 = hashlib.md5(news_url_bytes).hexdigest()

        screenshot_file = f"./docs/screenshots/press/{news_md5}.png"
        if not os.path.exists(screenshot_file):
            screenshot(news_url,news_md5)
            if not os.path.exists(screenshot_file):
                screenshot_line = '❌'
            else:
                screenshot_line = '[📸](https://images.ransomware.live/screenshots/press/'+news_md5+'.png)'
        else:
            stdlog('Screenshot ' +  news_md5 + ' already exist')
            screenshot_line = '[📸](https://images.ransomware.live/screenshots/press/'+news_md5+'.png)' 

        line = "| " + news_date + " | [`" + news_victim + "`](" + news_url + ") | " +  news_country + " | " + screenshot_line + " | "
        writeline(tweetspage, line)
        compteur += 1
    writeline(tweetspage, '')
    writeline(tweetspage, '📈 ' + str(compteur) + ' articles')
    writeline(tweetspage,' ')
    writeline(tweetspage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('recent news page generated')

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

pressmarkdown()
stdlog('ransomware.live: ' + 'Generating press markdown completed')

