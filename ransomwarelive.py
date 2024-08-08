#!/usr/bin/env python3
"""
Ransomware.live 

Description:
    Ransomware.live is a comprehensive command-line tool designed to manage and monitor ransomware activities.
    It supports various functionalities including scraping ransomware DLS (Dark Leak Sites), parsing the collected data,
    generating reports and graphs, taking screenshots of ransomware sites, and more.

    The program is built with extensibility in mind, allowing for easy addition of new features and integration with
    existing tools and libraries.

Usage:
    python3 ransomwarelive.py <command> [options]

Commands:
    scrape       Scrape ransomware DLS sites
    parse        Parse ransomware DLS sites
    generate     Generate Ransomware.live site
    screenshot   Generate screenshots for ransomware sites
    search       Search victim in the database
    rss          Generate RSS feed
    infostealer  Search for Hudsonrock database
    tools        Tools for Ransomware.live (subcommands: duplicate, order)

Options:
    -F, --force                 Force the execution of the command (e.g., force scraping)
    -g, --group <group_name>    Specify a specific group
    -u, --url <url>             Specify a specific URL for screenshots
    -v, --victim <victim_name>  Specify a victim name
    -d, --domain <domain_name>  Specify a domain name

Dependencies:
    - Python 3.x
    - Python packages: sys, os, asyncio, argparse, dotenv, hashlib, time, importlib, glob, datetime, atexit, tempfile

Environment Variables:
    - Managed via a `.env` file, which includes configurations for directories, data files, etc.

Author:
    Julien Mousqueton

Version:
    2.0.0
"""

import sys
import os
import asyncio
import argparse
from dotenv import load_dotenv 
import hashlib
import time
import importlib
import glob
from os.path import join, dirname, isfile, basename
from datetime import datetime 
## For lockfile
import atexit
import tempfile
import subprocess
import re

## Import Ransomware.live libs 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
import ransomwarelive 
from generatesite import writeline, month_name,month_digit
import generatesite 
import graph
import rss
import ransomnotes 
import hudsonrock
import negotiations

SOURCE='./source'


## Functions

def create_lock_file(LOCK_FILE):
    """Create a lock file to prevent multiple instances."""
    if os.path.exists(LOCK_FILE):
        print("Program is already running.")
        sys.exit(1)
    else:
        open(LOCK_FILE, 'w').close()
        atexit.register(remove_lock_file,LOCK_FILE)

def remove_lock_file(LOCK_FILE):
    """Remove the lock file on program exit."""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


def get_process_info():
    processes = []
    try:
        ps_output = subprocess.check_output(['ps', '-ef']).decode('utf-8')
        for line in ps_output.split('\n'):
            if 'python3 ransomwarelive.py' in line and any(proc in line for proc in ['scrape', 'parse', 'generate']):
                parts = line.split()
                process_name = parts[-1]
                process_id = parts[1]
                elapsed_seconds = int(subprocess.check_output(['ps', '-p', process_id, '-o', 'etimes=']).decode('utf-8').strip())
                elapsed_minutes = elapsed_seconds // 60
                processes.append((process_name, process_id, elapsed_minutes))
    except Exception as e:
        print(f"Error occurred: {e}")
    return processes

def process_parse_info(process_id, elapsed_minutes):
    try:
        lsof_output = subprocess.check_output(['lsof', '-p', process_id]).decode('utf-8')
        html_files = [line for line in lsof_output.split('\n') if '.html' in line]
        if html_files:
            for file in html_files:
                match = re.search(r'source/(.+?)-', file)
                if match:
                    group_name = match.group(1)
                    print(f"The \033[1mparse\033[0m process (PID: {process_id}) is running since {elapsed_minutes} minutes with group: \033[1m{group_name}\033[0m")
        else:
            print(f"The \033[1mparse\033[0m process (PID: {process_id}) is running since {elapsed_minutes} minutes, but no HTML files are currently open.")
    except Exception as e:
        print(f"Error occurred while processing 'parse': {e}")

def check_lock_file():
    lock_file_path = '/tmp/ransomwarelive.lock'
    if os.path.exists(lock_file_path):
        creation_time = os.path.getctime(lock_file_path)
        current_time = time.time()
        elapsed_seconds = int(current_time - creation_time)
        elapsed_minutes = elapsed_seconds // 60
        creation_time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creation_time))
        print(f"The \033[1mlock file\033[0m was created on: \033[1m{creation_time_formatted}\033[0m ({elapsed_minutes} minutes ago)")
    else:
        print("The \033[1mlock file\033[0m does not exist.")



if __name__ == '__main__':
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
     /  ************  \  Ransomware.live NG  /  ************  \ 
    --------------------                    --------------------
    '''
    )


    # Create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    # Create sub-parser for 'scrape'
    parser_scrape = subparsers.add_parser('scrape', help='Scrape ransomware DLS sites')
    parser_scrape.add_argument('-F', '--force', action='store_true', help='Force scraping')
    parser_scrape.add_argument('-g', '--group', type=str, help='Specify a specific group to scrape')

    # Create sub-parser for 'parse'
    parser_parse = subparsers.add_parser('parse', help='Parse ransomware DLS sites')
    parser_parse.add_argument('-g', '--group', type=str, help='Specify a specific group to parse')

    # Create sub-parser for 'generate'
    parser_generate = subparsers.add_parser('generate', help='Generate Ransomware.live site')

    parser_screenshot = subparsers.add_parser('screenshot', help='Generate screenshot for ransomware sites')
    parser_screenshot.add_argument('-g', '--group', type=str, help='Specify a specific group to screenshot')
    parser_screenshot.add_argument('-u', '--url', type=str, help='Specify a specific url to screenshot')

    parser_status = subparsers.add_parser('status', help='Show the status of ransomware.live')

    parser_search = subparsers.add_parser('search', help='Search victim in database')
    parser_search.add_argument('-v', '--victim', type=str, help='Specify a victim name')
    parser_search.add_argument('-d', '--domain', type=str, help='Specify a domain name')
    
    parser_rss = subparsers.add_parser('rss', help='Generate RSS feed')

    parser_infostealer = subparsers.add_parser('infostealer', help='Search for hudsonrock database')
    parser_infostealer.add_argument('-d', '--domain', type=str, help='Specify a victim domain')

    # Create sub-parser for 'tools'
    parser_tools = subparsers.add_parser('tools', help='Tools for Ransomware.live')
    tools_subparsers = parser_tools.add_subparsers(dest='tool_command')
    # Create sub-parser for 'tools duplicate'
    parser_tools_duplicate = tools_subparsers.add_parser('duplicate', help='Remove duplicate source files')
    parser_tools_order = tools_subparsers.add_parser('order', help='Order groups by alphabetic order')

    # Parse the arguments
    args = parser.parse_args()

    # Execute the appropriate function based on the provided subcommand
    if args.command == 'status':
        check_lock_file()
        processes = get_process_info()
        if processes:
            for process_name, process_id, elapsed_minutes in processes:
                bold_process_name = f"\033[1m{process_name}\033[0m"
                if process_name == 'parse':
                    process_parse_info(process_id, elapsed_minutes)
                else:
                    print(f"The {bold_process_name} process (PID: {process_id}) is running since {elapsed_minutes} minutes")
        else:
            print(" (!) None of the Ransomware.live processes are running")
    elif args.command == 'scrape':
        if args.group:
            asyncio.run(ransomwarelive.scrapegang(args.group,force=args.force))
        else: 
            LOCK_FILE_NAME = "scrape.lock"
            LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), LOCK_FILE_NAME)
            create_lock_file(LOCK_FILE_PATH)  
            start_time = time.time()
            asyncio.run(ransomwarelive.scrape(force=args.force))
            ransomwarelive.remove_duplicate_files(SOURCE)
            end_time = time.time()
            execution_time = end_time - start_time
            ransomwarelive.stdlog(f'Scraping execution time {execution_time:.2f} secondes')
            remove_lock_file(LOCK_FILE_PATH)
    elif args.command == 'parse':
        if args.group:
            ransomwarelive.stdlog('Parser : '+ args.group)
            module = importlib.import_module(f'parsers.{args.group}')
            module.main()
        else:
            LOCK_FILE_NAME = "parse.lock"
            LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), LOCK_FILE_NAME)
            create_lock_file(LOCK_FILE_PATH)  
            start_time = time.time()
            modules = sorted(glob.glob(join(dirname('parsers/'), "*.py")))
            __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
            counter = 0
            num_modules = len(__all__)
            for parser in __all__:
                counter += 1
                module = importlib.import_module(f'parsers.{parser}')
                ransomwarelive.stdlog('Parser : [' + str(counter) + '/' + str(num_modules) + '] '+ parser)
                module.main()
            end_time = time.time()
            execution_time = end_time - start_time
            ransomwarelive.stdlog(f'Parsing execution time {execution_time:.2f} secondes')
            remove_lock_file(LOCK_FILE_PATH)
    elif args.command == 'generate':
        LOCK_FILE_NAME = "generate.lock"
        LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), LOCK_FILE_NAME)
        create_lock_file(LOCK_FILE_PATH)  
        start_time = time.time()
        generatesite.mainpage()
        generatesite.statuspage()
        generatesite.summaryjson()
        load_dotenv()
        DATA_DIR = os.getenv('DATA_DIR')
        VICTIMS_FILE = os.getenv('VICTIMS_FILE')
        VICTIMS_FILE = DATA_DIR + VICTIMS_FILE
        if os.path.getmtime(VICTIMS_FILE) > (time.time() - 2700):
            ransomwarelive.stdlog('Victims database has been modified within the last 45 mins, assuming new posts discovered and generating full site')
            hudsonrockfile = DATA_DIR + 'hudsonrock.json'  
            data = ransomwarelive.openjson(hudsonrockfile)
            # Iterate through the entries and apply the conditions
            for key, value in data.items():
                if value['employees'] > 0 or value['users'] > 0:
                    generatesite.write_domain_info(key, value['employees'], value['users'], value['thirdparties'], value['employees_url'], value['users_url'], value['update'])
            generatesite.recentdiscoveredpage()
            generatesite.lastvictimspergroup()
            generatesite.profilepage()
            generatesite.groupprofilepage()
            year=datetime.now().year
            month=datetime.now().month
            graph.trend_posts_per_day()
            graph.plot_posts_by_group() 
            graph.pie_posts_by_group()
            ransomwarelive.stdlog('generating stats graph per month')
            graph.plot_victims_by_month()
            graph.plot_victims_by_month_cumulative()
            graph.plot_posts_by_group_past_7_days()
            ransomwarelive.stdlog('Creating graphs for '+ str(year))
            graph.pie_posts_by_group_by_year(2024)
            graph.plot_posts_by_group_by_year(2024)
            graph.trend_posts_per_day_2024()
            ransomwarelive.stdlog('generating stats page for ' +  str(year))
            currentgraph = 'docs/stats'+str(year)+'.md'
            with open(currentgraph, 'w', encoding='utf-8') as f:
                    f.close()
            writeline(currentgraph, '# Year '+ str(year) + ' in detail')
            writeline(currentgraph, '') 
            for month in range(1, month+1):
                    ransomwarelive.stdlog('generating stats section for ' +  month_name(month))
                    writeline(currentgraph, '') 
                    writeline(currentgraph, '## '+  month_name(month))
                    writeline(currentgraph, '') 
                    writeline(currentgraph, '| ![](graphs/postsbyday' + str(year) + month_digit(month) + '.png) | ![](graphs/postsbygroup' + str(year) + month_digit(month) + '.png) |')
                    writeline(currentgraph, '|---|---|')
                    writeline(currentgraph, '| ![](graphs/grouppie' + str(year) + month_digit(month) + '.png) |  ![](graphs/victims_per_day_' + str(year) + month_digit(month) + '.png)| ')
                    ransomwarelive.stdlog('generating graphs for ' + str(month) + '/' +  str(year))
                    graph.pie_posts_by_group_by_month(year,month)
                    graph.trend_posts_per_day_month(year,month)
                    graph.plot_posts_by_group_by_month(year,month)
                    graph.create_victims_per_day_graph(year,month)
            writeline(currentgraph, '')
            NowTime=datetime.now()
            writeline(currentgraph, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
            ransomwarelive.stdlog('stats for ' +  str(year) + ' generated')    
        else:
            ransomwarelive.stdlog('posts.json has not been modified within the last 45 mins, assuming no new posts discovered')
        base_url = "https://www.ransomware.live"
        GROUPS_FILE = os.getenv('GROUPS_FILE')
        GROUPS_FILE = DATA_DIR + GROUPS_FILE
        pages = ransomwarelive.openjson(GROUPS_FILE)
        note_directories = [directory for directory in os.listdir("./docs/notes/") if directory.lower() != ".git.md"]
        generatesite.generate_sitemapXML(base_url, pages, note_directories, output_file="./docs/sitemap.xml")
        ransomwarelive.stdlog('sitemap.xml generated')
        generatesite.generate_sitemapHTML(base_url, pages, note_directories, output_file="./docs/sitemap.html")
        ransomwarelive.stdlog('sitemap.html generated')
        ransomnotes.generate_ransom_notes()
        ransomwarelive.stdlog('Ransom Notes generated')
        for gang in negotiations.get_gangs('./import'):
            if gang not in ['./import/parsers', './import/.git']:
                negotiations.parse_group(gang)
        negotiations.generatenegotiationindex()
        ransomwarelive.stdlog('Ransomware Negotiation generated')
        end_time = time.time()
        execution_time = end_time - start_time
        ransomwarelive.stdlog(f'Generating execution time {execution_time:.2f} secondes')
        remove_lock_file(LOCK_FILE_PATH)

    elif args.command == 'screenshot':
        if args.group:
            print('TBC')
        elif args.url:
            load_dotenv()
            POST_SCREENSHOT_DIR = os.getenv('POST_SCREENSHOT_DIR')
            hash_object = hashlib.md5(args.url.encode('utf-8'))
            hex_digest = hash_object.hexdigest()
            filename = os.path.join(POST_SCREENSHOT_DIR, f'{hex_digest}.png')
            asyncio.run(ransomwarelive.screenshot(args.url,filename))
        else:
            asyncio.run(ransomwarelive.screenshotgangs())
    elif args.command =="search":
        if args.victim:
            ransomwarelive.searchvictim(args.victim)
        elif args.domain:
            ransomwarelive.searchvictim(args.domain,True)
        else:
            parser.print_help()
    elif args.command == "infostealer":
        if args.domain:
            hudsonrock.query_hudsonrock(args.domain)
        else:
            parser.print_help()  
    elif args.command =="rss":
        ransomwarelive.stdlog('Generate RSS Feed')
        rss.generate_rss_feed()
    elif args.command == 'tools' and args.tool_command == 'duplicate':
        ransomwarelive.remove_duplicate_files(SOURCE)
    elif args.command == 'tools' and args.tool_command == 'order':
        ransomwarelive.order_group()
    else:
        parser.print_help()