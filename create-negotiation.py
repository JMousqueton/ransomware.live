import json
import os
import glob
import logging
import sys
from datetime import datetime as dt

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO
    )

def stdlog(msg):
    '''standard infologging'''
    logging.info(msg)

def dbglog(msg):
    '''standard debug logging'''
    logging.debug(msg)

def errlog(msg):
    '''standard error logging'''
    logging.error(msg)

def honk(msg):
    '''critical error logging with termination'''
    logging.critical(msg)
    sys.exit()



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
        stdlog("[" + group_name + "] Processing " + name + " from file : " + file_name)

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
    <link rel="canonical" href="https://chat.ransomware.live">
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

            if party == 'Victim':
                codeHTML +=  '<p class="from-victim">' + content + '<br></br><i>' + timestamp + '</i></p>'
            else : 
                codeHTML += '<p class="from-gang">'  + content + '<br></br><i>' + timestamp + '</i></p>'
    
        codeHTML += '''
            </div></div><footer>
              <p id="Copyright">Source : <a href="https://github.com/Casualtek/Ransomchats" target=_blank>Valéry Marchive</a></p> 
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


def create_directory(directory_path):
    if not os.path.exists(directory_path.lower()):
        os.makedirs(directory_path.lower())

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

for gang in get_gangs('./data'):
    if gang not in ['./data/parsers', './data/.git']:
        parse_group(gang)
