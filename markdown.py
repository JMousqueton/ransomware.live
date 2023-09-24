#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, hashlib
import re
import time
import urllib.parse
from datetime import datetime as dt
#import datetime
from datetime import datetime, timedelta
from collections import Counter
import json

from sharedutils import gcount
from sharedutils import openjson
from sharedutils import postcount
from sharedutils import hostcount
from sharedutils import groupcount
from sharedutils import postssince
from sharedutils import parsercount
from sharedutils import onlinecount
from sharedutils import postslast24h
from sharedutils import poststhisyear
from sharedutils import postslastyear
from sharedutils import currentmonthstr
from sharedutils import monthlypostcount
from sharedutils import grouppostcount
from sharedutils import grouppostavailable
from sharedutils import postcountgroup
from sharedutils import countpostsyeartodate
# from sharedutils import stdlog, dbglog, errlog, honk
from sharedutils import stdlog
from plotting import trend_posts_per_day, plot_posts_by_group, pie_posts_by_group, plot_posts_by_group_past_7_days,trend_posts_per_day_2022, trend_posts_per_day_2023, plot_posts_by_group_by_year, pie_posts_by_group_by_year, pie_posts_by_group_by_month, trend_posts_per_day_month, plot_posts_by_group_by_month,plot_victims_by_month, plot_victims_by_month_cumulative
from plotting import create_victims_per_day_graph
from bs4 import BeautifulSoup


def find_matching_victims(victim_hidden):
    matching_pairs = ''
    if '*' not in victim_hidden:
        return matching_pairs
    matching_pairs = "Not Found"
    with open('posts.json', 'r') as json_file:
        data = json.load(json_file)
    victims = [entry['post_title'] for entry in data if entry['group_name'] == 'bianlian' and '*' not in entry['post_title']]
    for victim in victims:
            if len(victim) == len(victim_hidden):
                match = True
                for char1, char2 in zip(victim, victim_hidden):
                    if char2 != '*' and char1 != char2:
                        match = False
                        break
                if match:
                    stdlog("Victim: " + victim_hidden + "\t could be: "+ victim)
                    return(victim)

    return matching_pairs



def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(fmt, t):
    return t.strftime(fmt).replace('{S}', str(t.day) + suffix(t.day))

friendly_tz = custom_strftime('%B {S}, %Y', dt.now()).lower().capitalize()

NowTime=dt.now()



def directory_exists(directory):
    if os.path.exists(directory) and os.path.isdir(directory):
        return True
    else:
        return False

def writeline(file, line):
    '''write line to file'''
    with open(file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
        f.close()

def groupreport():
    '''
    create a list with number of posts per unique group
    '''
    stdlog('generating group report')
    posts = openjson('posts.json')
    # count the number of posts by group_name within posts.json
    group_counts = gcount(posts)
    # sort the group_counts - descending
    sorted_group_counts = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
    stdlog('group report generated with %d groups' % len(sorted_group_counts))
    return sorted_group_counts

def mainpage():
    '''
    main markdown report generator - used with github pages
    '''
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

    dir_path = r'/var/www/chat.ransomware.live/docs/chat'    
    # nbransom_notes=sum([len(folder) for r, d, folder in os.walk(dir_path)])-4
    nbsnego = 0
    for root, dirs, files in os.walk(dir_path):
        # Pour chaque fichier trouvé, on incrémente le compteur
        nbsnego += len(files)

    with open(uptime_sheet, 'w', encoding='utf-8') as f:
        f.close()
    # writeline(uptime_sheet, '## 📈 Ransomware.live')
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
    writeline(uptime_sheet, '      { "label": "In 2023", "value": ' + str(poststhisyear()) + '},')
    writeline(uptime_sheet, '      { "label": "In 2022", "value": ' + str(postslastyear()) + '}')
    # add coma to previous line 
    #writeline(uptime_sheet, '      { "label": "In 2022 (Year to date)", "value": ' + str(countpostsyeartodate()) + '}')
    writeline(uptime_sheet, '  ]')
    writeline(uptime_sheet, '}')
    writeline(uptime_sheet, '```')
    writeline(uptime_sheet, '📸 There are `' +  str(screenshots) + '` ransomware group host screenshots and `' + str(nbscreenshots) + '` post screenshots')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '📝 There are `' +  str(nbransom_notes) + '` ransomware notes and `' + str(nbsnego) +'` negotiation chats')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '⚙️ Ransomware.live has `' + str(parsercount()) + '` active parsers for indexing victims')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, 'So far, Ransomware.live has indexed `' + str(postcount()) + '` victims')

    with open('posts.json') as file:
        data = json.load(file)
    year = str(dt.today().year)
    # Filter the posts for the year 2023
    filtered_data = [post for post in data if post.get('published', '').startswith(year)]
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
    writeline(uptime_sheet,'  "title":   "🏆 Top 10 Ranwomware groups for ' + year +'",')
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

def statuspage():
    index_sheet = 'docs/status.md'
    with open(index_sheet, 'w', encoding='utf-8') as f:
        f.close()
    groups = openjson('groups.json')
    writeline(index_sheet, '')
    writeline(index_sheet, '## 🚦 All Groups')
    writeline(index_sheet, '')
    header = '| Group | Title | Status | Last seen | Location | Screenshot |'
    writeline(index_sheet, header)
    writeline(index_sheet, '|---|---|---|---|---|---|')
    for group in groups:
        stdlog('generating group report for ' + group['name'])
        for host in group['locations']:
            stdlog('generating host report for ' + host['fqdn'])
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
            line = '| [' + group['name'] + '](group/' + group['name'] + ') | ' + title + ' | ' + statusemoji + ' | ' + lastseen + ' | ' + host['fqdn'] + ' | ' + screen + ' | ' 
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
            stdlog('generating host report for ' + host['fqdn'])
            if host['available'] is True:
                if host['title'] is not None:
                    title = host['title'].replace('|', '-')
                else:
                    title = ''
                screenshot=host['fqdn'].replace('.', '-') + '.png'
                screen=''
                if os.path.exists('docs/screenshots/'+screenshot):
                    screen = '<a href="https://images.ransomware.live/screenshots/' + screenshot + '" target=_blank>📸</a>'
                line = '| [' + group['name'] + '](profiles.md?id=' + group['name'] + ') | ' + title + ' | ' + host['fqdn'] + ' | ' + screen + ' | ' 
                writeline(index_sheet, line)
    writeline(index_sheet, '')
    writeline(index_sheet, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    writeline(index_sheet, '')

def recentpublishedposts(top):
    '''
    create a list the last X posts (most recent)
    '''
    stdlog('finding recent posts')
    posts = openjson('posts.json')
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

def recentdiscoveredposts(top):
    '''
    create a list the last X posts (most recent)
    '''
    stdlog('finding recent posts')
    posts = openjson('posts.json')
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
    writeline(recentpage, '| Date | Title | Group | 📸 |')
    writeline(recentpage, '|---|---|---|---|')
    for post in recentpublishedposts(fetching_count):
        # show friendly date for discovered
        date = post['published'].split(' ')[0]
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
        line = '| ' + date + ' | [`' + title + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + grouplink + ' | ' + screenpost + ' |'
        writeline(recentpage, line)
    writeline(recentpage, '')
    writeline(recentpage, '> [!TIP] You can also check the 200 last victims sorted by discovered date by `Ransomware.live` [here](recentdiscoveredvictims.md).')
    writeline(recentpage, '')
    writeline(recentpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('recent published victims page generated')

def recentdiscoveredpage():
    '''create a markdown table for the last 200 posts based on the published value'''
    fetching_count = 200
    stdlog('generating recent discovered victims page')
    recentpage = 'docs/recentdiscoveredvictims.md'
    # delete contents of file
    with open(recentpage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(recentpage,'# Recent discovered victims by Ransomware.live')
    writeline(recentpage,'')
    writeline(recentpage, '> [!INFO] `Ransomware.live` provides tracking of ransomware groups and their victims. Descriptions available in the [group profiles view](profiles.md)')
    writeline(recentpage,'')
    writeline(recentpage, '**📰 200 last victims sorted by discovered date by `Ransomware.live`**')
    writeline(recentpage, '')
    writeline(recentpage, '| Discovered Date | Title | Group | 📸 |')
    writeline(recentpage, '|---|---|---|---|')
    for post in recentdiscoveredposts(fetching_count):
        # show friendly date for discovered
        date = post['published'].split(' ')[0]
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
        line = '| ' + date + ' | [`' + title + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + grouplink + ' | ' + screenpost + ' |'
        writeline(recentpage, line)
    writeline(recentpage, '')
    writeline(recentpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('recent published victims page generated')


def lastvictimspergroup():
    stdlog('generating last victims per group')
    page = 'docs/lastvictimspergroup.md'
    with open(page, 'w', encoding='utf-8') as f:
        f.close()
    # Load the data from the JSON files
    groups = openjson('groups.json')
    victims = openjson('posts.json')
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
    writeline(page, '')
    writeline(page, '# Last victims per Ransomware Group')
    writeline(page, '')
    writeline(page, '')
    writeline(page, '| Ransomware | Last Victim | Date | Status[<sup>*</sup>](lastvictimspergroup?id=-legend-) |')
    writeline(page, '|---|---|---|---|')
    # Print the last post title, published date, and website for each group with a last post
    for group_name, info in last_posts_info.items():
        if info['last_post_title'] != "No posts found": 
            if info['website']:
                website = info['website']
            else:
                search_query = urllib.parse.quote(info['last_post_title'])
                google_search_url = f"https://www.google.com/search?q={search_query}"
                website =  google_search_url
            writeline(page, '| [`' + group_name + '`](group/' + group_name +') |  ['+ info['last_post_title'] + '](' + website+ ') |' + info['published_date'] + ' |' + info['date_status'] + '|')
    writeline(page, '')
    writeline(page, '### <u> Legend : </u>  ')
    writeline(page, '')
    writeline(page, '🟢  less 3 months old')
    writeline(page, '')
    writeline(page, '🟠  between 3 months and 6 months old')
    writeline(page, '')
    writeline(page, '🔴  older than 6 months')
    writeline(page, '')
    writeline(page, '')
    writeline(page, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('Last victim per ransomware page generated')


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
    writeline(allpage, '💾 [Download](https://data.ransomware.live/posts.json) full list in **json** format')
    writeline(allpage, '')
    writeline(allpage, '💾 [Download](https://www.ransomware.live/posts.csv) full list in **csv** format')
    writeline(allpage, '')
    writeline(allpage, '')
    writeline(allpage, '| Date | Title | Group |')
    writeline(allpage, '|---|---|---|')
    posts = openjson('posts.json')
    sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
    for post in sorted_posts:
    # show friendly date for discovered
        date = post['published'].split(' ')[0]
        # replace markdown tampering characters
        title = post['post_title'].replace('|', '-')
        group = post['group_name'].replace('|', '-')
        urlencodedtitle = urllib.parse.quote_plus(title)
        grouplink = '[' + group + '](/group/' + group + ')'
        line = '| ' + date + ' | [`' + title + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + grouplink + ' |'
        writeline(allpage, line)
    writeline(allpage, '')
    writeline(allpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('all posts page generated')

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
    groups = openjson('groups.json')
    groupcpt=0
    for group in groups:
        writeline(profilepage, '## **' + group['name']+'**')
        try: 
            writeline(profilepage,'')
            writeline(profilepage,'> ' + group['description'].replace('\n',''))
            writeline(profilepage, '')
        except:
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
            posts = openjson('posts.json')
            sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
            filtered_posts = [post for post in sorted_posts if post['group_name'] == group['name']]
            last_10_posts = filtered_posts[:10]

            for post in last_10_posts:
                    try:    
                        description = re.sub(r"folder/.*", "folder/******", (post['description']))
                        description = re.sub(r".com/file/.*", ".com/file/******", description)
                        description = re.sub(r"anonfiles.com/.*/", "anonfiles.com/******/", description)
                        description = re.sub(r"dropmefiles.com/.* ","dropmefiles.com/******** ", description)
                    except:
                        description=' '
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
                        dt.strptime(date, '%Y-%m-%d')
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

def decryptiontools():
    '''
    create a page for Decryption Tools
    '''
    stdlog('generating decryption tools pages')
    decryptionpage = 'docs/decryption.md'
    # delete contents of file
    with open(decryptionpage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(decryptionpage, ' ')
    writeline(decryptionpage, '> [!TIP]')
    writeline(decryptionpage, '> Upload [HERE](https://id-ransomware.malwarehunterteam.com/index.php?lang=en_US) a ransom note and/or sample encrypted file to identify the ransomware that has encrypted your data.')
    writeline(decryptionpage, ' ')
    writeline(decryptionpage, ' ')
    writeline(decryptionpage,'!> IMPORTANT! Before downloading and starting the solution, read the how-to guide. Make sure you remove the malware from your system first, otherwise it will repeatedly lock your system or encrypt files. Any reliable antivirus solution can do this for you.')
    writeline(decryptionpage, '')
    writeline(decryptionpage, '')
    writeline(decryptionpage, '*Source : [No More Ransom](https://www.nomoreransom.org/en/decryption-tools.html)* is an initiative by the National High Tech Crime Unit of the Netherlands’ police, Europol’s European Cybercrime Centre, Kaspersky and McAfee')
    writeline(decryptionpage, '')
    # Définissez l'URL du fichier HTML à télécharger
    url = 'https://www.nomoreransom.org/en/decryption-tools.html'
    # Téléchargez le fichier HTML à l'aide de urllib.request.urlopen()
    with urllib.request.urlopen(url) as response:
        html_code = response.read()
    # Créez un objet BeautifulSoup àpartir du code HTML
    soup = BeautifulSoup(html_code, 'html.parser')
    # Sélectionnez la liste des ransomwares
    ransomware_list = soup.select('ul#ransomList li')
    # Pour chaque élément de la liste
    for li in ransomware_list:
    # Sélectionnez le nom du ransom
        ransom_name = li.select_one('h2 button')
        if ransom_name is not None:
            ransom_name = str(ransom_name)
            ransom_description = str(li.select_one('p'))
            author_name = str(li.select_one('p.small'))
            a_tags = li.find_all('a')
            download_link = str(li.select_one('a.button')['href'])
            howto = str(a_tags[0])
            veloute = BeautifulSoup(howto, 'html.parser')
            a_tag = veloute.find('a')
            linkhowto = a_tag['href']
            if linkhowto.startswith("http"):
                linkhowto = ' 📖  For more information please see this [how-to guide](' + str(linkhowto) +').'
            else:   
                linkhowto = ' 📖 For more information please see this [how-to guide](https://www.nomoreransom.org' + str(linkhowto) +').'           
            author_name = re.sub(r'<[^>]*>', '',author_name).replace('Tool made by  ','')
            writeline(decryptionpage, '## '+ re.sub(r'<[^>]*>', '',ransom_name))
            writeline(decryptionpage, '')
            writeline(decryptionpage, '> ' + re.sub(r'<[^>]*>', '',ransom_description ))
            writeline(decryptionpage, '')
            writeline(decryptionpage, str(linkhowto))
            writeline(decryptionpage, '')
            writeline(decryptionpage, '🌍 [' + author_name.rstrip() + '](' + download_link + ')')
            writeline(decryptionpage, '')
            writeline(decryptionpage, '---')
            writeline(decryptionpage, '')
    writeline(decryptionpage, '')
    writeline(decryptionpage,'_Source : [No More Ransom](https://www.nomoreransom.org/)_')
    writeline(decryptionpage, '')
    writeline(decryptionpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('decryption tools page generation complete')
   
def profile():
    '''
    create a profile page for each group in their unique markdown files within docs/profiles
    '''
    groups = openjson('groups.json')
    stdlog('generating profile pages for groups')
    groupcpt=0
    for group in groups:
        profilepage = 'docs/group/' + group['name'] + '.md'
        # delete contents of file
        with open(profilepage, 'w', encoding='utf-8') as f:
            f.close()
        writeline(profilepage, '# Profiles for ransomware group : **' + group['name']+'**')
        writeline(profilepage, '')
        try: 
            writeline(profilepage,'')
            writeline(profilepage,'> ' + group['description'].replace('\n',''))
            writeline(profilepage, '')
        except:
            writeline(profilepage, '')
        ## add notes if present
        if group['meta'] is not None:
            writeline(profilepage, '_`' + group['meta'] + '`_')
            writeline(profilepage, '')
        if len(group['profile']):
            writeline(profilepage, '### External analysis')
            for profile in group['profile'][:10]:
                writeline(profilepage, '- ' + profile)
                writeline(profilepage, '')
        if group['parser']:
            writeline(profilepage,'')
            writeline(profilepage,'🔎 `ransomware.live`has an active  parser for indexing '+ group['name']+'\'s victims')
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
        directory = '/var/www/ransomware.live/docs/negotiation/' + nego +'/'
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
            if group['name'] == 'bianlian':
                writeline(profilepage, '| victim | date | Description | possible victim | Screenshot | ')
                writeline(profilepage, '|---|---|---|---|---|')
            else:
                writeline(profilepage, '| victim | date | Description | Screenshot | ')
                writeline(profilepage, '|---|---|---|---|')
            posts = openjson('posts.json')
            sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
            for post in sorted_posts:
                if post['group_name'] == group['name']:
                    try:
                        description = re.sub(r"folder/.*", "folder/******", (post['description']))
                        description = re.sub(r".com/file/.*", ".com/file/******", description)
                        description = re.sub(r"anonfiles.com/.*/", "anonfiles.com/******/", description)
                        description = re.sub(r"dropmefiles.com/.* ","dropmefiles.com/******** ", description)
                        description = re.sub(r"view-files/.*", "view-files/********", description)
                    except:
                        description=' '
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
                        dt.strptime(date, '%Y-%m-%d')
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
                    if group['name'] == 'bianlian': 
                        line = '| ' + postURL + ' | ' + date + ' | ' + description + ' | ' + find_matching_victims(post['post_title']) + '|' + screenpost + ' |'
                    else:
                        line = '| ' + postURL + ' | ' + date + ' | ' + description + ' | ' + screenpost + ' |'
                    writeline(profilepage, line)
        writeline(profilepage, '')
        #writeline(profilepage,' --- ')
        writeline(profilepage, '')
        groupcpt +=1
        stdlog('[' + str(groupcpt) + '/' + str(groupcount()) + '] Write ' + group['name'] + ' profile page')
        writeline(profilepage, '')
        writeline(profilepage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('profile pages generation complete')

def mainsummaryjson():
    '''
    main markdown report generator - used with github pages
    '''
    stdlog('generating main page')
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
    writeline(uptime_sheet, '"poststhisyear": "' + str(poststhisyear()) + '",')
    writeline(uptime_sheet, '"currentyear": "' + str(dt.now().year) + '",')
    writeline(uptime_sheet, '"overallposts": "' + str(postcount())   + '"')
    writeline(uptime_sheet, '}')
    writeline(uptime_sheet, ']')

def month_name(month_number):
  months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
  return months[month_number - 1]

def month_digit(month_number):
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    return months[month_number - 1]

def main():
    stdlog('generating docs for '+str(groupcount()))
    year=datetime.now().year
    month=datetime.now().month 
    lastvictimspergroup()
    mainpage()
    statuspage()
    recentdiscoveredpage()
    recentpublishedpage()
    allposts()
    profilepage()
    profile()
    #if os.path.getmtime('docs/decryption.md') > (time.time() - 14400):
    #   try:
    #        decryptiontools()
    #   except:
    #       stdlog("decryptiontools failled")
    mainsummaryjson()
    # if posts.json has been modified within the last 45 mins, assume new posts discovered and recreate graphs
    if os.path.getmtime('posts.json') > (time.time() - 2700):
    #if True:
        stdlog('posts.json has been modified within the last 45 mins, assuming new posts discovered and recreating graphs')
        trend_posts_per_day()
        plot_posts_by_group() 
        pie_posts_by_group()
        stdlog('generating stats graph per month')
        plot_victims_by_month()
        plot_victims_by_month_cumulative()
        plot_posts_by_group_past_7_days()
        stdlog('Creating graphs for '+ str(year))
        pie_posts_by_group_by_year(2023)
        plot_posts_by_group_by_year(2023)
        trend_posts_per_day_2023()
        stdlog('generating stats page for ' +  str(year))
        currentgraph = 'docs/stats'+str(year)+'.md'
        with open(currentgraph, 'w', encoding='utf-8') as f:
                f.close()
        writeline(currentgraph, '# Year '+ str(year) + ' in detail')
        writeline(currentgraph, '') 
        for month in range(1, month+1):
                stdlog('generating stats section for ' +  month_name(month))
                writeline(currentgraph, '') 
                writeline(currentgraph, '## '+  month_name(month))
                writeline(currentgraph, '') 
                writeline(currentgraph, '| ![](graphs/postsbyday' + str(year) + month_digit(month) + '.png) | ![](graphs/postsbygroup' + str(year) + month_digit(month) + '.png) |')
                writeline(currentgraph, '|---|---|')
                writeline(currentgraph, '| ![](graphs/grouppie' + str(year) + month_digit(month) + '.png) |  ![](graphs/victims_per_day_' + str(year) + month_digit(month) + '.png)| ')
                stdlog('generating graphs for ' + str(month) + '/' +  str(year))
                pie_posts_by_group_by_month(year,month)
                trend_posts_per_day_month(year,month)
                plot_posts_by_group_by_month(year,month)
                create_victims_per_day_graph(year,month)
        writeline(currentgraph, '')
        writeline(currentgraph, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
        stdlog('stats for ' +  str(year) + ' generated')
    else:
        stdlog('posts.json has not been modified within the last 45 mins, assuming no new posts discovered')

'''
    Unused functions
'''


def profilepageOLD():
    '''
    create a profile page with each group in their unique markdown files within docs/profiles
    '''
    stdlog('generating profile pages')
    profilepage = 'docs/profiles.md'
    # delete contents of file
    with open(profilepage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(profilepage, '')
    groups = openjson('groups.json')
    groupcpt=0
    for group in groups:
        writeline(profilepage, '## **' + group['name']+'**')
        try: 
            writeline(profilepage,'')
            writeline(profilepage,'> ' + group['description'].replace('\n',''))
            writeline(profilepage, '')
        except:
            writeline(profilepage, '')
        if group['meta'] is not None:
            writeline(profilepage, '_`' + group['meta'] + '`_')
            writeline(profilepage, '')
        if len(group['profile']):
            writeline(profilepage, '### External analysis')
            for profile in group['profile']:
                writeline(profilepage, '- ' + profile)
                writeline(profilepage, '')
        if group['parser']:
            writeline(profilepage,'')
            writeline(profilepage,'🔎 `ransomware.live`has an active  parser for indexing '+ group['name']+'\'s victims')
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
        directory = '/var/www/chat.ransomware.live/docs/chat/' + nego +'/'
        if directory_exists(directory):
            writeline(profilepage, '')
            writeline(profilepage, '### Negotiation chats')
            writeline(profilepage, '')
            writeline(profilepage, '| Name | Link |')
            writeline(profilepage, '|---|---|')
            for filename in sorted(os.listdir(directory)):
                line = '|' + os.path.splitext(filename)[0].replace('_','.') + '| <a href="https://chat.ransomware.live/chat/'+ nego + '/' + filename + '" target=_blank> 💬 </a> |'
                writeline(profilepage, line)
            writeline(profilepage, '')
        
        ### GRAPH
        if os.path.exists('docs/graphs/stats-'+group['name']+'.png'):
            writeline(profilepage, '')
            writeline(profilepage, '### Total Attacks Over Time')
            writeline(profilepage, '')
            writeline(profilepage,'![Statistics](/graphs/stats-' + group['name'] + '.png)') 
            writeline(profilepage, '')

        ### POSTS 
        writeline(profilepage, '')
        writeline(profilepage, '### Victims')
        writeline(profilepage, '')
        writeline(profilepage, '> ' + grouppostcount(group['name']))
        writeline(profilepage, '')
        if grouppostavailable(group['name']):
            writeline(profilepage, '| post | date | Description | Screenshot | ')
            writeline(profilepage, '|---|---|---|---|')
            posts = openjson('posts.json')
            sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
            filtered_posts = [post for post in sorted_posts if post['group_name'] == group['name']]
            last_10_posts = filtered_posts[:10]

            for post in last_10_posts:
                    try:    
                        description = re.sub(r"folder/.*", "folder/******", (post['description']))
                        description = re.sub(r".com/file/.*", ".com/file/******", description)
                        description = re.sub(r"anonfiles.com/.*/", "anonfiles.com/******/", description)
                        description = re.sub(r"dropmefiles.com/.* ","dropmefiles.com/******** ", description)
                        description = re.sub(r"view-files/.*", "view-files/********", description)
                    except:
                        description=' '
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
                        datetime.datetime.strptime(date, '%Y-%m-%d')
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
