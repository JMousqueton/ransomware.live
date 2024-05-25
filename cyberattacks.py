import json 
import logging
from datetime import datetime as dt
from dotenv import load_dotenv
import os,hashlib
from urllib.parse import urlparse
import requests
import deepl
from sharedutils import stdlog, errlog
# For screenshot 
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
# For watermark on screenshot 
from PIL import Image
from PIL import ImageDraw

load_dotenv()
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO
    )

NowTime=dt.now()


def screenshot(webpage,output,delay=15000,option=None):
    stdlog('webshot: {}'.format(webpage))
    if webpage.endswith(".pdf"):
        stdlog("PDF file no screenshot")
        return
    disabled_site = ["hk01.com", "mb.com.ph", "tass.ru", "richmond-news.com", "ncic.co.jp","guardian.co.tt","theadvocate.com","jaccs.co.jp","azimut.it","lapresse.ca","noirlab","wlox.com","cdn-api.markitdigital.com","unimedia","jamaica-gleaner","myrgv.com", "nypost.com", "www.cbc.ca", "star-", "timesnews", "focus-wtv", "itatiaia", "telegraph.co.uk", "nj1015", "illawarramercury", "radio-canada","eet-china","majorcadailybulletin"]
    if any(website in webpage for website in disabled_site):
        stdlog("Disabled screenshot for website : "+ webpage)
        return  # This will exit the function
    name = 'docs/screenshots/news/' + output + '.png'
    with sync_playwright() as play:
                try:
                    if option in ['exception']:
                        #browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                        browser = play.firefox.launch(
                          args=["--headless=new"])
                        print('(!) exception')
                    else:
                        browser = play.chromium.launch(
                            args=["--headless=new"])
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
                #browser.close()



def openjson(url):
    '''
    opens a file and returns the json as a dict
    '''
    #url = "https://raw.githubusercontent.com/Casualtek/Cyberwatch/main/cyberattacks.json" 
    response = requests.get(url)
    data = json.loads(response.text)
    return data



def writeline(file, line):
    '''write line to file'''
    with open(file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
        f.close()

def recentnews(top):
    '''
    create a list the last X posts (most recent)
    '''
    stdlog('finding recent news')
    attacks = openjson('https://raw.githubusercontent.com/Casualtek/Cyberwatch/main/cyberattacks.json')
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
    


def getnews():
    '''
    create a list the last X posts (most recent)
    '''
    stdlog('finding all news')
    recentnews=[]
    attacks = openjson('https://raw.githubusercontent.com/Casualtek/Cyberwatch/main/cyberattacks.json')
    # sort the posts by timestamp - descending
    sorted_attacks = sorted(attacks, key=lambda x: x['date'], reverse=True)
    # create a list of the last X posts
    recentnews = []
    for attack in sorted_attacks:
        recentnews.append(attack)
    stdlog('recent news generated')
    return recentnews


def country2flag(pays):
    match pays[:3]:
        case "SWE":
            flag="SE"
        case "URY":
            flag="UY"
        case "MEX":
            flag="MX"
        case "PRT":
            flag="PT"
        case "SVN":
            flag="SI"
        case "IRL":
            flag="IE"
        case "MTQ":
            flag="FR"
        case "AUT":
            flag="AT"
        case "CHL":
            flag="CL"
        case "UK":
            flag="GB"
        case "JAM":
            flag="JM"
        case "POL":
            flag="PL"
        case "DNK":
            flag="DK"
        case "CPV":
            flag="CV"
        case _:
            flag=pays[:2]
    return "![" + pays + "](https://images.ransomware.live/flags/"+flag+".svg  ':size=32x24 :no-zoom')"

def translate_text(text):
    translator = deepl.Translator(DEEPL_API_KEY)
    result     = translator.translate_text(text , target_lang='EN-US')
    return result.text

def recentcyberattacks():
    stdlog('Generating news markdown')
    tweetspage = 'docs/recentcyberattacks.md'
    fetching_count = 100
    # delete contents of file
    with open(tweetspage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(tweetspage,' ')
    writeline(tweetspage, '# Last 100 cyberattacks')
    writeline(tweetspage, ' ')
    writeline(tweetspage, '_reported by [Valéry Marchive](https://twitter.com/ValeryMarchive)_')
    writeline(tweetspage, ' ')
    writeline(tweetspage, '> [!INFO]')
    writeline(tweetspage, '> `Valéry Marchive` works in the technology industry as a journalist. He is the editor-in-chief of [LeMagIT](https://www.lemagit.fr). He also comments and analyzes ransomware attacks on [social media](https://twitter.com/valerymarchive?lang=en).')
    writeline(tweetspage,' ')
    writeline(tweetspage, '> [!TIP]Check [here](allcyberattacks) for 🎯 all cyberattacks')
    writeline(tweetspage, ' ')
    writeline(tweetspage,'   ')
    writeline(tweetspage, ' ')
    writeline(tweetspage, '| Date | Country | Victim | Source | Screenshot | ')
    writeline(tweetspage, '|---|---|---|---|---|')
    compteur = 0  # Initialisation du compteur à 0
    for tweet in recentnews(fetching_count):
        news_date = tweet['date']
        news_victim = tweet['victim'] 
        try: 
            news_country = tweet['country'] 
        except: 
            news_country = tweet['Country']
        #try:
        #    news_title = tweet['title']
        #except:
        #    news_title = "N/A"
        #news_summary = tweet['summary'] 
        news_url= tweet['url']  
        parsed_url = urlparse(news_url)
        news_source = parsed_url.netloc

    
        # Calculate the MD5 checksum of the "post_url" value
        news_url_bytes = news_url.encode('utf-8')
        news_md5 = hashlib.md5(news_url_bytes).hexdigest()

        screenshot_file = f"./docs/screenshots/news/{news_md5}.png"
        if not os.path.exists(screenshot_file):
            screenshot(news_url,news_md5)
            if not os.path.exists(screenshot_file):
                screenshot_line = '❌'
                if news_url.endswith(".pdf"):
                    screenshot_line = '[📄](' + news_url + ')'

            else:
                screenshot_line = '[📸](https://images.ransomware.live/screenshots/news/'+news_md5+'.png)'
        else:
            stdlog('Screenshot ' +  news_md5 + ' already exist')
            screenshot_line = '[📸](https://images.ransomware.live/screenshots/news/'+news_md5+'.png)' 

        #line = "| " + news_date + " | " + country2flag(news_country) + " | [`" + news_victim.replace("La victime est ","") + "`](https://google.com/search?q=" + news_victim.replace(" ","%20") + ") | [" +  news_source.replace("www.","") + "](" + news_url + ") | " + screenshot_line + " | "
        line = "| " + news_date + " | " + country2flag(news_country) + " | [`" + news_victim.replace("La victime est ","") + "`](https://" + tweet['domain'] + ") | [" +  news_source.replace("www.","") + "](" + news_url + ") | " + screenshot_line + " | "
        writeline(tweetspage, line)
        compteur += 1
    writeline(tweetspage, '> \nSource : [Github Casualtek/Cyberwatch](https://github.com/Casualtek/Cyberwatch/)')
    writeline(tweetspage, '')
    writeline(tweetspage, 'Check [🎯 All cyberattacks](allcyberattacks)')
    writeline(tweetspage,' ')
    writeline(tweetspage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('recent news page generated')



def allcyberattacks():
    stdlog('Generating all news markdown')
    tweetspage = 'docs/allcyberattacks.md'
    # delete contents of file
    with open(tweetspage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(tweetspage,' ')
    writeline(tweetspage, '# All cyberattacks')
    writeline(tweetspage, ' ')
    writeline(tweetspage, '_reported by [Valéry Marchive](https://twitter.com/ValeryMarchive)_')
    writeline(tweetspage, ' ')
    writeline(tweetspage, '> [!INFO]')
    writeline(tweetspage, '> `Valéry Marchive` works in the technology industry as a journalist. He is the editor-in-chief of [LeMagIT](https://www.lemagit.fr). He also comments and analyzes ransomware attacks on [social media](https://twitter.com/valerymarchive?lang=en).')
    writeline(tweetspage, '> \nSource : [Github Casualtek/Cyberwatch](https://github.com/Casualtek/Cyberwatch/)')
    writeline(tweetspage, ' ')
    writeline(tweetspage, '| Date | Country | Victim | Source | Screenshot | ')
    writeline(tweetspage, '|---|---|---|---|---|')
    compteur = 0  # Initialisation du compteur à 0
    for tweet in getnews():
        news_date = tweet['date']
        news_victim = tweet['victim'] 
        news_country = tweet['country'] 
        news_url = tweet['url']  
        parsed_url = urlparse(news_url)
        news_source = parsed_url.netloc

    
        # Calculate the MD5 checksum of the "post_url" value
        news_url_bytes = news_url.encode('utf-8')
        news_md5 = hashlib.md5(news_url_bytes).hexdigest()

        screenshot_file = f"./docs/screenshots/news/{news_md5}.png"
        if not os.path.exists(screenshot_file):
                screenshot_line = '❌'
                if news_url.endswith(".pdf"):
                    screenshot_line = '[📄](' + news_url + ')'

        else:
            screenshot_line = '[📸](https://images.ransomware.live/screenshots/news/'+news_md5+'.png)' 

        #line = "| " + news_date + " | " + country2flag(news_country) + " | [`" + translate_text(news_victim.replace("La victime est ","")) + "`](https://google.com/search?q=" + news_victim.replace(" ","%20") + ") | [" +  news_source.replace("www.","") + "](" + news_url + ") |"
        #line = "| " + news_date + " | " + country2flag(news_country) + " | [`" + news_victim.replace("La victime est ","") + "`](https://google.com/search?q=" + news_victim.replace(" ","%20") + ") | [" +  news_source.replace("www.","") + "](" + news_url + ") | " + screenshot_line + " | "
        line = "| " + news_date + " | " + country2flag(news_country) + " | [`" + news_victim.replace("La victime est ","") + "`](https://" + tweet['domain'] + ") | [" +  news_source.replace("www.","") + "](" + news_url + ") | " + screenshot_line + " | "
        writeline(tweetspage, line)
        compteur += 1
    writeline(tweetspage, '')
    writeline(tweetspage, '📈 ' + str(compteur) + ' cyberattacks')
    writeline(tweetspage,' ')
    writeline(tweetspage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('all news page generated')

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

recentcyberattacks()
allcyberattacks()
stdlog('ransomware.live: ' + 'Generating news markdown completed')
