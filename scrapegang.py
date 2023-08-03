# from ast import parse
import os,sys
import json
from datetime import datetime

import os
from bs4 import BeautifulSoup

# local imports
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from sharedutils import striptld
from sharedutils import openjson
from sharedutils import getsitetitle
from sharedutils import stdlog, dbglog, errlog


def scraper(querygroup=''):
    '''main scraping function'''
    groups = openjson("groups.json")
    stdlog('scraper: ' + 'looking for ' + querygroup)
    # iterate each provider
    for group in groups:
        if group['name'] == querygroup:      
            stdlog('scraper: ' + 'working on ' + querygroup)
            # iterate each location/mirror/relay
            for host in group['locations']:
                stdlog('ransomwatch: ' + 'scraping ' + host['slug']) 
                if host['version'] == 3 or host['version'] == 0:
                # here 
                    try:
                        with sync_playwright() as play:
                                if querygroup in ['blackbasta','everest']:
                                    stdlog('exception for ' + querygroup)
                                    browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                                        args=['--unsafely-treat-insecure-origin-as-secure='+host['slug']])
                                else:
                                    browser = play.chromium.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                                        args=['--unsafely-treat-insecure-origin-as-secure='+host['slug']])    
                                context = browser.new_context(ignore_https_errors= True )
                                page = context.new_page()
                                if 'timeout' in host and host['timeout'] is not None:
                                   page.goto(host['slug'], wait_until='load', timeout = host['timeout']*1000)
                                else:
                                    page.goto(host['slug'], wait_until='load', timeout = 120000)
                                page.bring_to_front()
                                delay = host['delay']*1000 if ( 'delay' in host and host['delay'] is not None ) \
                                    else 15000
                                if delay != 15000:
                                    stdlog('New delay : ' + str(delay) + 'ms')
                                page.wait_for_timeout(5000)
                                #page.wait_for_timeout(delay)
                                page.mouse.move(x=500, y=400)
                                page.wait_for_load_state('networkidle')
                                page.mouse.wheel(delta_y=2000, delta_x=0)
                                page.wait_for_load_state('networkidle')
                                page.wait_for_timeout(delay)
                                filename = group['name'] + '-' + str(striptld(host['slug'])) + '.html'
                                name = os.path.join(os.getcwd(), 'source', filename)
                                with open(name, 'w', encoding='utf-8') as sitesource:
                                    sitesource.write(page.content())
                                    sitesource.close()
                                    host['available'] = True
                                    host['title'] = getsitetitle(name)
                                    host['lastscrape'] = str(datetime.today())            
                                    host['updated'] = str(datetime.today())
                                    dbglog('ransomwatch: ' + 'scrape successful')
                                    with open('groups.json', 'w', encoding='utf-8') as groupsfile:
                                        json.dump(groups, groupsfile, ensure_ascii=False, indent=4)
                                        groupsfile.close()
                                        dbglog('scraper: ' + 'groups.json updated')
                                browser.close()
                    except PlaywrightTimeoutError:
                        stdlog('Timeout!')
                    except Exception as exception:
                        errlog(exception)
                        errlog("error")
                stdlog('leaving : ' + host['slug'] + ' --------- ' + group['name'])
        

def main():
    groupname = sys.argv[1]
    scraper(groupname)



if __name__ == '__main__':
    main()

