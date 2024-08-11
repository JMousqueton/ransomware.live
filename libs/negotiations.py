import json
import os
import re
import glob
import logging
import sys
from datetime import datetime as dt
from ransomwarelive import stdlog, errlog
from generatesite import writeline

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
    return time_difference.days < 2

def parse_group(group_name):

    # Specify the directory path
    directory_path = group_name
    stdlog('Processing Group : ' + group_name )
    group_name = os.path.basename(os.path.normpath(directory_path))
    create_directory('./docs/negotiation/' + group_name.lower())
    # Use glob to get all files with .json extension
    json_files = glob.glob(os.path.join(directory_path, '*.json'))

    
    # Process each JSON file
    for file_path in json_files:
        # Extract the file name without extension
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        # Replace underscores with dots
        name = file_name.replace('_', '.')

        # Print the modified file name
        #stdlog("[" + group_name + "] Processing " + name + " from file : " + file_name)

        with open(file_path) as file:
            data = json.load(file)

        codeHTML = f'''
            <!DOCTYPE html>
            <!--
            ██████╗  █████╗ ███╗   ██╗███████╗ ██████╗ ███╗   ███╗██╗    ██╗ █████╗ ██████╗ ███████╗   ██╗     ██╗██╗   ██╗███████╗
            ██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔═══██╗████╗ ████║██║    ██║██╔══██╗██╔══██╗██╔════╝   ██║     ██║██║   ██║██╔════╝
            ██████╔╝███████║██╔██╗ ██║███████╗██║   ██║██╔████╔██║██║ █╗ ██║███████║██████╔╝█████╗     ██║     ██║██║   ██║█████╗  
            ██╔══██╗██╔══██║██║╚██╗██║╚════██║██║   ██║██║╚██╔╝██║██║███╗██║██╔══██║██╔══██╗██╔══╝     ██║     ██║╚██╗ ██╔╝██╔══╝  
            ██║  ██║██║  ██║██║ ╚████║███████║╚██████╔╝██║ ╚═╝ ██║╚███╔███╔╝██║  ██║██║  ██║███████╗██╗███████╗██║ ╚████╔╝ ███████╗
            ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝  ╚══════╝
            version 2023-04 
            by Julien Mousqueton https://julien.io 
            -->
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <title>{group_name} Negotiations</title>
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <meta name="description" content="Ransomware.live : Ransomware Groups {group_name} Negotiations">
  <meta name="keywords" content="ransomware, breach, leak, post, gang, data, cybersecurity, victims, ransom, julien, mousqueton, julien mousqueton, CyberSoc, CTI, negotiation, ransom">
  <!-- Open Graph / Facebook -->
   <meta property="og:type" content="website">
   <meta property="og:url" content="https://chat.ransomware.live">
   <meta property="og:title" content="Ransomware.live 👀">
   <meta property="og:description" content="Ransomware.live : Ransomware Groups {group_name} Negotiations">
   <meta property="og:image" content="https://chat.ransomware.live/ransomware.png">
  <!-- Twitter -->
   <meta property="twitter:card" content="summary_large_image">
   <meta property="twitter:url" content="https://chat.ransomware.live/">
   <meta property="twitter:title" content="Ransomware.live 👀">
   <meta property="twitter:description" content="Ransomware.live : Ransomware Groups {group_name} Negotiations">
   <meta property="twitter:image" content="https://chat.ransomware.live/ransomware.png">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
    <link rel="canonical" href="https://www.ransomware.live">
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
     <link rel="stylesheet" href="https://static.ransomware.live/negotiation.css"></head><body><div class="container">
     '''
        codeHTML += '''
 <style>
      /* Remove the border from the link */
    .logo-link {
      text-decoration: none;
      border: none;
    }
    #Copyright {
        font-size: 15px;
        font-weight: bold;
        font-family: 'Comic Sans MS', cursive;
        color: #808080; /* Darker text color */
        margin-top: 15px;
        margin-bottom: 10px;
        text-align: center;
    }

    #Copyright a {
        text-decoration: none;
    }

    #Copyright a:visited {
        color: #808080;
    }
    #Copyright2 {
         font-size: 15px;
        font-weight: bold;
        /* font-family: 'Comic Sans MS', cursive; $/ 
        color: #808080; /* Darker text color */
        margin-top: 15px;
        margin-bottom: 10px;
        text-align: center;
    }

    #Copyright2 a {
        text-decoration: none;
    }

    #Copyright2 a:visited {
        color: #808080;
    }
  </style>
</head>
<body>
            '''

        if group_name == 'lockbit3.0': 
            id='lockbit3'
        else:
            id=group_name
        chat_id = data['chat_id'] 
        try:
            date_object = dt.strptime(chat_id, "%Y%m%d")
            chat_id = 'Date: ' + date_object.strftime("%Y-%m-%d")
        except:
            pass

        if data['chat_id'] == '':
           try:
                date_object = dt.strptime(name[:8], "%Y%m%d")
                chat_id = 'Date: ' + date_object.strftime("%Y-%m-%d")
           except:
               pass


        codeHTML += '<h1>💬 Negotiation with <a href="https://www.ransomware.live/#/group/' +  id.lower() + '">' + group_name + '</a></h1><BR>'
        codeHTML += '<h2> ID: ' + name + '</h2>' 
        codeHTML += '<p class="comment">' + chat_id + '</p><div class="imessage">'

        for message in data['messages']:
            party = message['party']
            content = message['content']
            timestamp = message['timestamp']
            if party.lower() == 'victim' or party.replace(' ','').lower() == 'client':
                codeHTML +=  '<p class="from-victim">' + content + '<br></br><i>' + timestamp + '</i></p>'
            else : 
                codeHTML += '<p class="from-gang">'  + content + '<br></br><i>' + timestamp + '</i></p>'
    
        codeHTML += '''
            </div></div><footer>
              <p id="Copyright">Source : <a href="https://github.com/Casualtek/Ransomchats" target=_blank>Valéry Marchive</a> and Ransomware.live</p> 
              <p id="Copyright2"><a href="https://www.ransomware.live" target=_self>&copy 2024 Ransomware.live</a></p> 
            </footer></body></html>
    '''

        with open('./docs/negotiation/' + group_name.lower() + '/' + file_name+'.html', 'w') as output:
            # Write the variable's value to the file
            output.write(codeHTML)
        
def get_gangs(directory_path):
    directories = []
    for entry in os.listdir(directory_path):
        entry_path = os.path.join(directory_path, entry)
        if os.path.isdir(entry_path):
            directories.append(entry_path)
    return directories

def est_domaine(chaine):
#    pattern = r'^[a-zA-Z0-9-]{1,63}\.[a-zA-Z]{2,63}$'
    pattern = r'^[a-zA-Z0-9-]{1,63}(?:\.[a-zA-Z0-9-]{1,63})*\.[a-zA-Z]{2,63}$'
    match = re.match(pattern, chaine)
    return bool(match)


def create_directory(directory_path):
    if not os.path.exists(directory_path.lower()):
        os.makedirs(directory_path.lower())

def generatenegotiationindex():
    stdlog('Generating negotiations markdown')
    negopage = './docs/negotiations.md'
    compteur = 0
    # delete contents of file
    with open(negopage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(negopage,'')
    writeline(negopage, '# 💬 Negotiation with ransomware groups')
    writeline(negopage,'')
    writeline(negopage, '_by [Valéry Marchive](https://twitter.com/ValeryMarchive)_')
    writeline(negopage,'')
    writeline(negopage, '> [!INFO]')
    writeline(negopage, '> `Valéry Marchive` works in the technology industry as a journalist. He is the editor-in-chief of [LeMagIT](https://www.lemagit.fr). He also comments and analyzes ransomware attacks on [social media](https://twitter.com/valerymarchive?lang=en).')
    writeline(negopage,' ')
    writeline(negopage, '> [!TIP]')
    writeline(negopage, '> Some amount are expressed only with cryptocurrency. The price in USD is based on the cryptocurrency market at the time of the negotiation.')
    writeline(negopage,' ')
    #writeline(negopage,'   ')
    #writeline(negopage, '> [!WARNING]')
    #writeline(negopage, '> The analysis of the neogiciations is still in progress ...')
    #writeline(negopage,' ')
    writeline(negopage, '| Ransomware | Name | # Msg | Chat | Initial Ransom | Negotiated Ransom | Paid |')
    writeline(negopage, '|---|---|---|---|---|---|---|')
    
    directory_path = './docs/negotiation'

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
            if is_file_less_than_days_old('./import/'+dir_name+'/'+chat_name+'.json'):
                note = '  🆕' 
            else:
                note ='' 

            with open('./import/'+dir_name+'/'+chat_name+'.json') as srcfile:
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
            metafile = './import/'+dir_name+'/'+chat_name+'.meta'
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
            writeline(negopage,'| [' + group_name + '](group/' + link + ')  | ' +  name + ' ' + note  + ' | ' + str(count) + ' | <a href="/#/negotiation/' + group_name + '/' + chat_name + '.html"> 💬 </a> | '+ endofline)
    
    writeline(negopage, '')
    writeline(negopage, '📈 ' + str(compteur) + ' negotiation chats')
    writeline(negopage,' ')
    writeline(negopage, '> \nSource : [Github Casualtek/Ransomchats](https://github.com/Casualtek/Ransomchats/)')
    writeline(negopage,' ')
    writeline(negopage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')

