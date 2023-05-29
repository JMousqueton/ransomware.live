#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, hashlib
import re
import time
import urllib.parse
from datetime import datetime as dt
import datetime

from sharedutils import gcount
from sharedutils import openjson
from sharedutils import postcount
from sharedutils import hostcount
from sharedutils import groupcount
from sharedutils import postssince
from sharedutils import parsercount
from sharedutils import onlinecount
from sharedutils import postslast24h
# from sharedutils import version2count
from sharedutils import poststhisyear
from sharedutils import postslastyear
from sharedutils import currentmonthstr
from sharedutils import monthlypostcount
from sharedutils import grouppostcount
from sharedutils import grouppostavailable
# from sharedutils import headlesscount
# from sharedutils import countcaptchahosts
# from sharedutils import stdlog, dbglog, errlog, honk
from sharedutils import stdlog
from plotting import trend_posts_per_day, plot_posts_by_group, pie_posts_by_group, plot_posts_by_group_past_7_days,trend_posts_per_day_2022, trend_posts_per_day_2023, plot_posts_by_group_by_year, pie_posts_by_group_by_year, pie_posts_by_group_by_month, trend_posts_per_day_month, plot_posts_by_group_by_month
from bs4 import BeautifulSoup

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(fmt, t):
    return t.strftime(fmt).replace('{S}', str(t.day) + suffix(t.day))

friendly_tz = custom_strftime('%B {S}, %Y', dt.now()).lower()

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
    # nbransom_notes=sum([len(folder) for r, d, folder in os.walk(dir_path)])-4
    nbransom_notes = 0
    for root, dirs, files in os.walk(dir_path):
        # On ignore le répertoire .git
        if ".git" in dirs:
            dirs.remove(".git")
        # Pour chaque fichier trouvé, on incrémente le compteur
        nbransom_notes += len(files)
    dir_path = r'docs/screenshots/posts'
    # nbransom_notes=sum([len(folder) for r, d, folder in os.walk(dir_path)])-4
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
    writeline(uptime_sheet,'---')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet,'> A **ransomware** is a type of malware used by cybercriminals to encrypt the victim\'s files and make them inaccessible unless they pay the ransom. Today cybercriminals are more sophisticated, and they not only encrypt the victim\'s files also they leaking their data to the Darknet unless they will pay the ransom.')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet, '>[!NOTE]')
    writeline(uptime_sheet, '>_`Ransomware.live` is collecting, indexing, and centralizing ransomware information from most ransomware groups and their victims. The information posted on this website is dynamically updated in near real-time._')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet, '### Some figures ')
    writeline(uptime_sheet,'')
    writeline(uptime_sheet, '🔎 Currently tracking `' + str(groupcount()) + '` groups across `' + str(hostcount()) + '` relays & mirrors - _`' + str(onlinecount()) + '` currently online_ 🟢')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, 'Check recent ransomware posts [`here`](recentposts.md)')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '⏰ There have been `' + str(postslast24h()) + '` posts within the `last 24 hours`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '🕓 There have been `' + str(monthlypostcount()) + '` posts within the `month of ' + currentmonthstr() + '`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '📅 There have been `' + str(postssince(90)) + '` posts within the `last 90 days`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '🏚 There have been `' + str(poststhisyear()) + '` posts since the `1st January ' + str(dt.now().year) + '`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '📸 There are `' +  str(screenshots) + '` ransomware group host screenshots and `' + str(nbscreenshots) + '` post screenshots')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '📝 There are `' +  str(nbransom_notes) + '` ransomware notes and `' + str(nbsnego) +'` negotiation chats')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '🚀 There have been `' + str(postslastyear()) + '` posts `last year`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '🐣 There have been `' + str(postcount()) + '` posts `since the dawn of ransomware.live`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '⚙️ There are `' + str(parsercount()) + '` custom parsers indexing posts')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '')
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
            line = '| [' + group['name'] + '](profiles.md?id=' + group['name'] + ') | ' + title + ' | ' + statusemoji + ' | ' + lastseen + ' | ' + host['fqdn'] + ' | ' + screen + ' | ' 
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





#def sidebar():
#    '''
#    create a sidebar markdown report NOT USED 
#    '''
#    stdlog('generating sidebar')
#    sidebar = 'docs/_sidebar.md'
#    # delete contents of file
#    with open(sidebar, 'w', encoding='utf-8') as f:
#        f.close()
#    writeline(sidebar, '- [home](README.md)')
#    writeline(sidebar, '- [group index](INDEX.md)')
#    writeline(sidebar, '- [recent posts](recentposts.md)')
#    writeline(sidebar, '- [stats & graphs](stats.md)')
#    writeline(sidebar, '- [group profiles](profiles.md)')
#    stdlog('sidebar generated')

#def statspage():
#    '''
#    create a stats page in markdown containing the matplotlib graphs
#    '''
#    stdlog('generating stats page')
#    statspage = 'docs/stats.md'
#    # delete contents of file
#    with open(statspage, 'w', encoding='utf-8') as f:
#        f.close()
#    writeline(statspage, '# 📊 stats')
#    writeline(statspage, '')
#    #writeline(statspage, '_timestamp association commenced october 2021_')
#    #writeline(statspage, '')
#    writeline(statspage, '| ![](graphs/postsbygroup7days.png) | ![](graphs/postsbyday.png) |')
#    writeline(statspage, '|---|---|')
#    writeline(statspage, '![](graphs/postsbygroup.png) | ![](graphs/grouppie.png) |')
#    writeline(statspage, '')
#    writeline(statspage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
#    stdlog('stats page generated')

def recentposts(top):
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

def recentpage():
    '''create a markdown table for the last 200 posts based on the discovered value'''
    fetching_count = 200
    stdlog('generating recent posts page')
    recentpage = 'docs/recentposts.md'
    # delete contents of file
    with open(recentpage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(recentpage,'')
    writeline(recentpage, '> `Ransomware.live` provides tracking of ransomware groups and their victims. Descriptions available in the [group profiles view](profiles.md)')
    writeline(recentpage,'')
    writeline(recentpage, '**📰 200 last posts**')
    writeline(recentpage, '')
    writeline(recentpage, '| Date | Title | Group | 📸 |')
    writeline(recentpage, '|---|---|---|---|')
    for post in recentposts(fetching_count):
        # show friendly date for discovered
        date = post['published'].split(' ')[0]
        # replace markdown tampering characters
        title = post['post_title'].replace('|', '-')
        group = post['group_name'].replace('|', '-')
        urlencodedtitle = urllib.parse.quote_plus(title)
        grouplink = '[' + group + '](profiles.md?id=' + group + ')'
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
    stdlog('recent posts page generated')

def allposts():
    '''create a markdown table for all posts '''
    stdlog('generating allposts page')
    allpage = 'docs/allposts.md'
    # delete contents of file
    with open(allpage, 'w', encoding='utf-8') as f:
        f.close()
    # writeline(allpage, '# 📰 All posts')
    writeline(allpage, '')
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
        grouplink = '[' + group + '](profiles.md?id=' + group + ')'
        line = '| ' + date + ' | [`' + title + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + grouplink + ' |'
        writeline(allpage, line)
    writeline(allpage, '')
    writeline(allpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('all posts page generated')


def profilepage():
    '''
    create a profile page for each group in their unique markdown files within docs/profiles
    '''
    stdlog('generating profile pages')
    profilepage = 'docs/profiles.md'
    # delete contents of file
    with open(profilepage, 'w', encoding='utf-8') as f:
        f.close()
    #writeline(profilepage, '# Profiles')
    writeline(profilepage, '')
    groups = openjson('groups.json')
    for group in groups:
        writeline(profilepage, '## **' + group['name']+'**')
        try: 
            writeline(profilepage,'')
            writeline(profilepage,'> ' + group['description'].replace('\n',''))
            writeline(profilepage, '')
        except:
            writeline(profilepage, '')
        #if group['captcha'] is True:
        #    writeline(profilepage, ':warning: _has a captcha_')
        #    writeline(profilepage, '')
        #if group['parser'] is True:
        #    writeline(profilepage, '_parsing : `enabled`_')
        #    writeline(profilepage, '')
        #else:
        #    writeline(profilepage, '_parsing : `disabled`_')
        #    writeline(profilepage, '')
        # add notes if present
        if group['meta'] is not None:
            writeline(profilepage, '_`' + group['meta'] + '`_')
            writeline(profilepage, '')
        #if group['javascript_render'] is True:
        #    writeline(profilepage, '> fetching this site requires a headless browser')
        #    writeline(profilepage, '')
        if len(group['profile']):
            writeline(profilepage, '### External analysis')
            for profile in group['profile']:
                writeline(profilepage, '- ' + profile)
                writeline(profilepage, '')
        writeline(profilepage, '### URLs')
        writeline(profilepage, '| Title | Available | Last visit | fqdn | Screenshot ')
        writeline(profilepage, '|---|---|---|---|---|')        
        for host in group['locations']:
            if host['available'] is True:
                statusemoji = '🟢'
            elif host['available'] is False:
                statusemoji = '🔴'
                # lastseen = host['lastscrape'].split(' ')[0]
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
        ransom_notes = ''
        directory = 'docs/ransomware_notes/' + group['name'] +'/'
        if directory_exists(directory):
            for filename in sorted(os.listdir(directory)):
                # stdlog(filename)
                cpt_note += 1
                ransom_notes = ransom_notes + ' <a href="/ransomware_notes/' +group['name'] + '/' + filename + '" target=_blank>#' + str(cpt_note) + '</a> ' 
                # stdlog('add ' + str(cpt_note) + 'note(s) to '+ group['name'] )
            writeline(profilepage, '')        
        if cpt_note > 0:
            writeline(profilepage, '')
            writeline(profilepage, '### Ransom note')
            writeline(profilepage,'* 📝 Ransom notes : ' + ransom_notes)
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
            writeline(profilepage, '### Negotiations')
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
        writeline(profilepage, '### Posts')
        writeline(profilepage, '')
        writeline(profilepage, '> ' + grouppostcount(group['name']))
        writeline(profilepage, '')
        if grouppostavailable(group['name']):
            writeline(profilepage, '| post | date | Description | Screenshot | ')
            writeline(profilepage, '|---|---|---|---|')
            posts = openjson('posts.json')
            sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
            for post in sorted_posts:
                if post['group_name'] == group['name']:
                    try:
                        description = re.sub(r"folder/.*", "folder/******", (post['description']))
                        description = re.sub(r".com/file/.*", ".com/file/******", description)
                        description = re.sub(r"anonfiles.com/.*/", "anonfiles.com/******/", description)
                    except:
                        description=' '
                    #if post['website'] is not None: 
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
                            screenpost='<a href="https://images.ransomware.live/screenshots/posts/' + hex_digest + '.png" target=_blank>📸</a>'
                    line = '| ' + postURL + ' | ' + date + ' | ' + description + ' | ' + screenpost + ' |'
                    writeline(profilepage, line)
        writeline(profilepage, '')
        #writeline(profilepage, '')
        #writeline(profilepage, '[⤴️](profiles?id=group-profiles)')
        #writeline(profilepage, '')
        writeline(profilepage,' --- ')
        writeline(profilepage, '')
        stdlog('profile page for ' + group['name'] + ' generated')
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
    writeline(decryptionpage, '')
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
    for group in groups:
        stdlog('generating profile page for '+ group['name'])
        profilepage = 'docs/profiles/' + group['name'] + '.md'
        # delete contents of file
        with open(profilepage, 'w', encoding='utf-8') as f:
            f.close()
        writeline(profilepage, '# Profiles')
        writeline(profilepage, '')
        writeline(profilepage, '## **' + group['name']+'**')
        try: 
            writeline(profilepage,'')
            writeline(profilepage,'> ' + group['description'].replace('\n',''))
            writeline(profilepage, '')
        except:
            writeline(profilepage, '')
        #if group['captcha'] is True:
        #    writeline(profilepage, ':warning: _has a captcha_')
        #    writeline(profilepage, '')
        if group['parser'] is True:
            writeline(profilepage, '_Parser : `Available`_')
            writeline(profilepage, '')
        else:
            writeline(profilepage, '_Parser : `Not available`_')
            writeline(profilepage, '')
        # add notes if present
        if group['meta'] is not None:
            writeline(profilepage, '_`' + group['meta'] + '`_')
            writeline(profilepage, '')
        #if group['javascript_render'] is True:
        #    writeline(profilepage, '> fetching this site requires a headless browser')
        #    writeline(profilepage, '')
        if len(group['profile']):
            writeline(profilepage, '### External analysis')
            for profile in group['profile']:
                writeline(profilepage, '- ' + profile)
                writeline(profilepage, '')
        writeline(profilepage, '### URLs')
        writeline(profilepage, '| Title | Available | Last visit | fqdn | Screenshot ')
        writeline(profilepage, '|---|---|---|---|---|')        
        for host in group['locations']:
            if host['available'] is True:
                statusemoji = '🟢'
            elif host['available'] is False:
                statusemoji = '🔴'
                # lastseen = host['lastscrape'].split(' ')[0]
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
        ransom_notes = ''
        directory = 'docs/ransomware_notes/' + group['name'] +'/'
        if directory_exists(directory):
            for filename in sorted(os.listdir(directory)):
                # stdlog(filename)
                cpt_note += 1
                ransom_notes = ransom_notes + ' <a href="/ransomware_notes/' +group['name'] + '/' + filename + '" target=_blank>#' + str(cpt_note) + '</a> ' 
                # stdlog('add ' + str(cpt_note) + 'note(s) to '+ group['name'] )
            writeline(profilepage, '')        
        if cpt_note > 0:
            writeline(profilepage, '')
            writeline(profilepage, '### Ransom note')
            writeline(profilepage,'* 📝 Ransom notes : ' + ransom_notes)
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
            writeline(profilepage, '### Negotiations')
            writeline(profilepage, '')
            writeline(profilepage, '| Name | Link |')
            writeline(profilepage, '|---|---|')
            for filename in sorted(os.listdir(directory)):
                line = '|' + os.path.splitext(filename)[0] + '| <a href="https://chat.ransomware.live/chat/'+ nego + '/' + filename + '" target=_blank> 💬 </a> |'
                writeline(profilepage, line)
            writeline(profilepage, '')

        ### POSTS 
        writeline(profilepage, '')
        writeline(profilepage, '### Posts')
        writeline(profilepage, '')
        writeline(profilepage, '> ' + grouppostcount(group['name']))
        writeline(profilepage, '')
        if grouppostavailable(group['name']):
            writeline(profilepage, '| post | date | Description')
            writeline(profilepage, '|---|---|---|')
            posts = openjson('posts.json')
            sorted_posts = sorted(posts, key=lambda x: x['published'], reverse=True)
            for post in sorted_posts:
                if post['group_name'] == group['name']:
                    try:
                        description = re.sub(r"folder/.*", "folder/******", (post['description']))
                        description = re.sub(r".com/file/.*", ".com/file/******", description)
                        description = re.sub(r"anonfiles.com/.*/", "anonfiles.com/******/", description)
                    except:
                        description=' '
                    #if post['website'] is not None: 
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
                    date = date.split('-')
                    date = date[2] + '/' + date[1] + '/' + date[0]
                    line = '| ' + postURL + ' | ' + date + ' | ' + description + ' |'
                    writeline(profilepage, line)
        writeline(profilepage, '')
        #writeline(profilepage, '')
        #writeline(profilepage, '[⤴️](profiles?id=group-profiles)')
        #writeline(profilepage, '')
        writeline(profilepage,' --- ')
        writeline(profilepage, '')
        stdlog('profile page for ' + group['name'] + ' generated')
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
    stdlog('generating docs')
    year=datetime.datetime.now().year
    month=datetime.datetime.now().month 
    mainpage()
    statuspage()
    recentpage()
    allposts()
    profilepage()
    profile()
    if os.path.getmtime('docs/decryption.md') < (time.time() - 14400):
        decryptiontools()
    mainsummaryjson()
    # if posts.json has been modified within the last 45 mins, assume new posts discovered and recreate graphs
    if os.path.getmtime('posts.json') > (time.time() - 2700):
        stdlog('posts.json has been modified within the last 45 mins, assuming new posts discovered and recreating graphs')
        trend_posts_per_day()
        plot_posts_by_group() 
        pie_posts_by_group()
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
                writeline(currentgraph, '| ![](graphs/grouppie' + str(year) + month_digit(month) + '.png) | | ')
                stdlog('generating graphs for ' + str(month) + '/' +  str(year))
                pie_posts_by_group_by_month(year,month)
                trend_posts_per_day_month(year,month)
                plot_posts_by_group_by_month(year,month)
        writeline(currentgraph, '')
        writeline(currentgraph, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
        stdlog('stats for ' +  str(year) + ' generated')
    else:
        stdlog('posts.json has not been modified within the last 45 mins, assuming no new posts discovered')
