#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
🧅 👀 🦅 👹
ransomwatch
does what it says on the tin
'''
# from ast import parse
import os, hashlib
import json
import argparse
from datetime import datetime
import importlib
from os.path import dirname, basename, isfile, join
import time
# local imports

# import parsers
from markdown import main as markdown

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_sync

from sharedutils import striptld
from sharedutils import openjson
from sharedutils import checktcp
from sharedutils import siteschema
# from sharedutils import socksfetcher
from sharedutils import getsitetitle
from sharedutils import getonionversion
from sharedutils import postsjson2cvs
from sharedutils import sockshost, socksport
from sharedutils import stdlog, dbglog, errlog, honk
import glob


start_time = time.time()
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
     /  ************  \     ransomwhat?      /  ************  \ 
    --------------------                    --------------------
    '''
)

parser = argparse.ArgumentParser(description='👀  ransomwatch')
parser.add_argument("--name", help='provider name')
parser.add_argument("--location", help='onionsite fqdn')
parser.add_argument("--append", help='add onionsite fqdn to existing record')
parser.add_argument("--force", help='force to scrape disable sites')
parser.add_argument(
    "mode",
    help='operation to execute',
    choices=['add', 'append', 'scrape', 'parse', 'list', 'markdown', 'check']
    )
args = parser.parse_args()

if args.mode == ('add' or 'append') and (args.name is None or args.location is None):
    parser.error("operation requires --name and --location")

if args.mode == 'check' and args.location is None:
    parser.error("operation requires --location")

if args.location:
    # if args.location ends in .onion
    if args.location.endswith('.onion'):
        siteinfo = getonionversion(args.location)
        if siteinfo[0] is None:
            parser.error("location does not appear to be a v2 or v3 onionsite")
    else:
        errlog("location does not appear to be an onionsite, assuming clearnet")

def creategroup(name, location):
    '''
    create a new group for a new provider - added to groups.json
    '''
    location = siteschema(location)
    insertdata = {
        'name': name,
        'captcha': bool(),
        'parser': bool(),
        'javascript_render': bool(),
        'meta': None,
        'description': None,
        'locations': [
            location
        ],
        'profile': list()
    }
    return insertdata

# check if a given location exists in groups.json
if args.mode == 'check':
    groups = openjson("groups.json")
    for group in groups:
        for location in group['locations']:
            if location['fqdn'] == args.location:
                print('ransomwatch: ' + 'location ' + args.location + ' is in groups.json')
                exit()
    print('ransomwatch: ' + 'location ' + args.location + ' is not in groups.json')
    exit()

def checkexisting(provider):
    '''
    check if group already exists within groups.json
    '''
    groups = openjson("groups.json")
    for group in groups:
        if group['name'] == provider:
            return True
    return False

def scraper(force=''):
    '''main scraping function'''
    groups = openjson("groups.json")
    # iterate each provider
    for group in groups:
        stdlog('ransomwatch: ' + 'working on ' + group['name'])
        # iterate each location/mirror/relay
        for host in group['locations']:
            stdlog('ransomwatch: ' + 'scraping ' + host['slug'])
            host['available'] = bool()
            '''
            only scrape onion v3 unless using headless browser, not long before this will not be possible
            https://support.torproject.org/onionservices/v2-deprecation/
            '''  
            if host['enabled'] is False:
                if (force !='1'):
                    stdlog('ransomwatch: ' + 'skipping, this host has been flagged as disabled')
                    continue
                else:
                    stdlog('ransomwatch: ' + 'forcing, this host has been flagged as disabled')
            if host['version'] == 3 or host['version'] == 0:
                # here 
                try:
                    with sync_playwright() as play:
                            if group['name'] in ['blackbasta', 'clop', 'metaencryptor','bianlian']:
                                browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                                    args=['--unsafely-treat-insecure-origin-as-secure='+host['slug'], "--headless=new"])
                            elif group['name'] in ['ransomed']:
                                 browser = play.firefox.launch(args=['--unsafely-treat-insecure-origin-as-secure='+host['slug']])
                            elif group['name'] in ['knight','lockbit3']:
                                browser = play.chromium.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                                    args=['--unsafely-treat-insecure-origin-as-secure='+host['slug'], "--headless=new"])
                            else:
                                browser = play.chromium.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                                    args=['--unsafely-treat-insecure-origin-as-secure='+host['slug'], "--headless=new"])
                            context = browser.new_context(ignore_https_errors= True )
                            page = context.new_page()
                            stealth_sync(page)
                            if 'timeout' in host and host['timeout'] is not None:
                               page.goto(host['slug'], wait_until='load', timeout = host['timeout']*1000)
                            else:
                                page.goto(host['slug'], wait_until='load', timeout = 120000)
                            page.bring_to_front()
                            delay = host['delay']*1000 if ( 'delay' in host and host['delay'] is not None ) \
                                else 15000
                            if delay != 15000:
                                stdlog('New delay : ' + str(delay) + 'ms')
                            page.wait_for_timeout(delay)
                            page.mouse.move(x=500, y=400)
                            page.wait_for_load_state('networkidle')
                            page.mouse.wheel(delta_y=2000, delta_x=0)
                            page.wait_for_load_state('networkidle')
                            page.wait_for_timeout(5000)
                            #filename = group['name'] + '-' + str(striptld(host['slug'])) + '.html'
                            hash_object = hashlib.md5()
                            hash_object.update(host['slug'].encode('utf-8'))
                            hex_digest = hash_object.hexdigest()
                            filename = group['name'] + '-' + hex_digest + '.html'
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
                                    dbglog('ransomwatch: ' + 'groups.json updated')
                            browser.close()
                except PlaywrightTimeoutError:
                    stdlog('Timeout!')
                except Exception as exception:
                    stdlog(exception)
                stdlog('leaving : ' + host['slug'] + ' --------- ' + group['name'])

### END 

def adder(name, location):
    '''
    handles the addition of new providers to groups.json
    '''
    if checkexisting(name):
        stdlog('ransomwatch: ' + 'records for ' + name + ' already exist, appending to avoid duplication')
        appender(args.name, args.location)
    else:
        groups = openjson("groups.json")
        newrec = creategroup(name, location)
        groups.append(dict(newrec))
        with open('groups.json', 'w', encoding='utf-8') as groupsfile:
            json.dump(groups, groupsfile, ensure_ascii=False, indent=4)
        stdlog('ransomwatch: ' + 'record for ' + name + ' added to groups.json')

def appender(name, location):
    '''
    handles the addition of new mirrors and relays for the same site
    to an existing group within groups.json
    '''
    groups = openjson("groups.json")
    success = bool()
    for group in groups:
        if group['name'] == name:
            group['locations'].append(siteschema(location))
            success = True
    if success:
        with open('groups.json', 'w', encoding='utf-8') as groupsfile:
            json.dump(groups, groupsfile, ensure_ascii=False, indent=4)
    else:
        honk('cannot append to non-existing provider')

def lister():
    '''
    basic function to list out groups & addresses to term
    '''
    groups = openjson("groups.json")
    for group in groups:
        for host in group['locations']:
            print(group['name'] + ' - ' + host['slug'])

if args.mode == 'scrape':
    if not checktcp(sockshost, socksport):
        honk("socks proxy not available and required for scraping!")
    scraper(args.force)
    stdlog('ransomwatch: ' + 'scrape run complete')

if args.mode == 'add':
    adder(args.name, args.location)

if args.mode == 'append':
    appender(args.name, args.location)

if args.mode == 'markdown':
    markdown()
    stdlog('ransomwatch: ' + 'markdown run complete')

if args.mode == 'parse':
    modules = sorted(glob.glob(join(dirname('parsers/'), "*.py")))
    __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
    counter = 0
    num_modules = len(__all__)
    for parser in __all__:
        counter += 1
        module = importlib.import_module(f'parsers.{parser}')
        stdlog('Parser : [' + str(counter) + '/' + str(num_modules) + '] '+ parser)
        module.main()

    stdlog('ransomwatch: ' + 'parse run complete')
    postsjson2cvs()
    stdlog('ransomwatch: ' + 'convert json to csv run complete')

if args.mode == 'list':
    lister()
 
end_time = time.time()
elapsed_time = end_time - start_time
stdlog(f"Script executed in {elapsed_time:.4f} seconds")
