#!/usr/bin/env python3

import subprocess
import re
import os
import time
import json

def get_process_info():
    processes = []
    try:
        ps_output = subprocess.check_output(['ps', '-ef']).decode('utf-8')
        for line in ps_output.split('\n'):
            if 'python3 ransomwatch.py' in line and any(proc in line for proc in ['scrape', 'parse', 'markdown']):
                parts = line.split()
                process_name = parts[-1]
                process_id = parts[1]
                elapsed_seconds = int(subprocess.check_output(['ps', '-p', process_id, '-o', 'etimes=']).decode('utf-8').strip())
                elapsed_minutes = elapsed_seconds // 60
                processes.append((process_name, process_id, elapsed_minutes))
            if 'python3 countries.py' in line:
                parts = line.split()
                process_name = parts[-1].replace('.py','')
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

def find_scraped_group(process_id,elapsed_minutes):
    try:
        # Load the group.json file
        with open('groups.json', 'r') as f:
            group_data = json.load(f)
        
        ps_output = subprocess.check_output(['ps', '-ef']).decode('utf-8')
        for line in ps_output.split('\n'):
            if '/root/.cache/ms-playwright/chromium-1033/chrome-linux/chrome' in line:
                #match = re.search(r'(http[s]?://\S+\.onion)', line)
                match = re.search(r'(http[s]?://\S+)', line)
                if match:
                    onion_address = match.group(1)
                    group_name = 'Unknown group'
                    for group in group_data:
                        for location in group.get('locations', []):
                            if location.get('fqdn') in onion_address:
                                group_name = group['name']
                                break
                        if group_name != 'Unknown group':
                            break
                    print(f"The \033[1mscrape\033[0m process is running (PID: {process_id}) since {elapsed_minutes} minutes")
                    print(f"  Processing gang: \033[1m{group_name}\033[0m")
                else:
                    print(f"The \033[1mscrape\033[0m process is running since {elapsed_minutes} minutes")
                    print("No group name found.")
                break
    except Exception as e:
        print(f"Error occurred while finding scraped group: {e}")

def main():
    check_lock_file()
    processes = get_process_info()

    if processes:
        for process_name, process_id, elapsed_minutes in processes:
            bold_process_name = f"\033[1m{process_name}\033[0m"
            if process_name == 'parse':
                process_parse_info(process_id, elapsed_minutes)
            elif process_name == 'scrape':
                find_scraped_group(process_id,elapsed_minutes)
            else:
                print(f"The {bold_process_name} process (PID: {process_id}) is running since {elapsed_minutes} minutes")
    else:
        print(" (!) None of the Ransomware.live processes are running")

if __name__ == "__main__":
    main()
