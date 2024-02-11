import json, re
import logging
from datetime import datetime as dt
import os,hashlib

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO
    )

NowTime=dt.now()


def get_file_date(file_path):
    stat = os.stat(file_path)
    timestamp = stat.st_mtime
    file_date = dt.fromtimestamp(timestamp)
    return file_date

def is_file_less_than_days_old(file_path):
    file_date = get_file_date(file_path)
    current_date = dt.now()
    time_difference = current_date - file_date
    return time_difference.days < 3

def openjson(url):
    '''
    opens a file and returns the json as a dict
    '''
    #url = "https://raw.githubusercontent.com/Casualtek/Cyberwatch/main/cyberattacks.json" 
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

def est_domaine(chaine):
#    pattern = r'^[a-zA-Z0-9-]{1,63}\.[a-zA-Z]{2,63}$'
    pattern = r'^[a-zA-Z0-9-]{1,63}(?:\.[a-zA-Z0-9-]{1,63})*\.[a-zA-Z]{2,63}$'
    match = re.match(pattern, chaine)
    return bool(match)

def tweetmarkdown():
    stdlog('Generating negotiations markdown')
    tweetspage = 'docs/negotiations.md'
    compteur = 0
    # delete contents of file
    with open(tweetspage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(tweetspage,'')
    writeline(tweetspage, '# 💬 Negotiation with ransomware groups')
    writeline(tweetspage,'')
    writeline(tweetspage, '_by [Valéry Marchive](https://twitter.com/ValeryMarchive)_')
    writeline(tweetspage,'')
    writeline(tweetspage, '> [!INFO]')
    writeline(tweetspage, '> `Valéry Marchive` works in the technology industry as a journalist. He is the editor-in-chief of [LeMagIT](https://www.lemagit.fr). He also comments and analyzes ransomware attacks on [social media](https://twitter.com/valerymarchive?lang=en).')
    writeline(tweetspage,' ')
    writeline(tweetspage, '> [!TIP]')
    writeline(tweetspage, '> Some amount are expressed only with cryptocurrency. The price in USD is based on the cryptocurrency market at the time of the negotiation.')
    writeline(tweetspage,' ')
    #writeline(tweetspage,'   ')
    #writeline(tweetspage, '> [!WARNING]')
    #writeline(tweetspage, '> The analysis of the neogiciations is still in progress ...')
    #writeline(tweetspage,' ')
    writeline(tweetspage, '| Ransomware | Name | # Msg | Chat | Initial Ransom | Negotiated Ransom | Paid |')
    writeline(tweetspage, '|---|---|---|---|---|---|---|')
    
    directory_path = '/var/www/ransomware.live/docs/negotiation'

    # Get a sorted list of all directories within the main directory
    directories = sorted([name for name in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, name))])

    # Iterate over each directory
    for group_name in directories:
        group_directory = os.path.join(directory_path, group_name)

        # Get a sorted list of all files within the current directory
        files = sorted([name for name in os.listdir(group_directory) if os.path.isfile(os.path.join(group_directory, name))])

        # Iterate over each file and print its name without extension
        for chat_file in files:
            chat_name = os.path.splitext(chat_file)[0]  # Get the file name without extension
            compteur += 1
            if group_name=='lockbit3.0':
                link='lockbit3'
            else:
                link=group_name
            match group_name:
                case 'lockbit3.0': 
                    dir_name = group_name
                case 'mount-locker':
                    dir_name = group_name
                case 'blackmatter':
                    dir_name = 'BlackMatter'
                case 'revil':
                    dir_name = 'REvil'
                case 'blackbasta':
                    dir_name = 'BlackBasta'
                case _:
                    dir_name = group_name.capitalize()
            if is_file_less_than_days_old('/var/www/ransomware.live/data/'+dir_name+'/'+chat_name+'.json'):
                note = '  🆕' 
            else:
                note ='' 

            with open('/var/www/ransomware.live/data/'+dir_name+'/'+chat_name+'.json') as srcfile:
                    data = json.load(srcfile)
            chat_id = data['chat_id'].replace('\n',' ')
            count = sum(1 for message in data['messages'] if 'content' in message)

            try:
                date_object = dt.strptime(chat_id, "%Y%m%d")
                chat_id = 'Date: ' + date_object.strftime("%Y-%m-%d")
            except:
                pass
            if data['chat_id'] == '':
                try:
                    date_object = dt.strptime(chat_name[:8], "%Y%m%d")
                    chat_id = 'Date: ' + date_object.strftime("%Y-%m-%d") 
                except:
                    pass
            metafile = '/var/www/ransomware.live/data/'+dir_name+'/'+chat_name+'.meta'
            if os.path.isfile(metafile):
                with open(metafile, 'r') as file:
                    content = file.read().strip()
                values = content.split(';')  # Split the content using semicolon as the delimiter
                paid = ''
                try: 
                    if values[2].lower() == 'paid':
                        paid = '💸'
                except:
                    pass
                endofline = ' ' +  values[0] + ' | '+ values[1] +' |'+ paid  + '|'
            else:
                endofline ='|||'


            if est_domaine(chat_name.replace('_','.')):
                    name = '[`' + chat_name.replace('_','.') + '`](https://www.'+ chat_name.replace('_','.') + ')'
            else:
                name = chat_name.replace('_','.')
            # writeline(tweetspage,'| [' + group_name + '](group/' + link + ')  | ' +  name + ' ' + note + ' | ' + chat_id + ' | ' + str(count) + ' | <a href="/#/negotiation/' + group_name + '/' + chat_name + '.html"> 💬 </a> | '+ endofline)
            writeline(tweetspage,'| [' + group_name + '](group/' + link + ')  | ' +  name + ' ' + note  + ' | ' + str(count) + ' | <a href="/#/negotiation/' + group_name + '/' + chat_name + '.html"> 💬 </a> | '+ endofline)
            


    
    writeline(tweetspage, '')
    writeline(tweetspage, '📈 ' + str(compteur) + ' negotiation chats')
    writeline(tweetspage,' ')
    writeline(tweetspage, '> \nSource : [Github Casualtek/Ransomchats](https://github.com/Casualtek/Ransomchats/)')
    writeline(tweetspage,' ')
    writeline(tweetspage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('Negotiations page generated')

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

tweetmarkdown()
stdlog('ransomware.live: ' + 'Generating neogitations markdown completed')

