import os, datetime, sys, re
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from shared_utils import appender, errlog

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))



def main():
    script_path = os.path.abspath(__file__)
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        group_name = os.path.basename(original_path).replace('.py','')
    else:
        group_name = os.path.basename(script_path).replace('.py','')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name + '-'):
                html_doc = tmp_dir / filename
                with open(html_doc, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')


                divs_name=soup.find_all('table', {"class": "table table-bordered table-content"})
                # <table class="table table-bordered table-content ">
                for div in divs_name:
                    title = div.find('h1').text.strip()
                    description = div.find('p').text.strip().replace("\n", "")
                    website = div.find('a')
                    website = website.attrs['href']
                    appender(title, 'blackbyte', description,website)
                file.close()
        except:
                pass
        try:
            if filename.startswith('blackbyte-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                tables = soup.find_all('table', class_='table')

                # Extract captions and last dates
                for table in tables:
                   caption = table.find('caption', class_='target-name').text
                   rows = table.find('tbody').find_all('tr')
                   last_date = rows[-1].find('td').text
                   #print(f"Table Caption: {caption}")
                   #print(f"Last Date: {last_date}")
                   last_date = datetime.strptime(last_date, '%Y-%m-%d %H:%M')
                   published = last_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                   appender(caption, 'blackbyte', '','',published)
        except Exception as e:
            errlog('blackbyte: ' + 'parsing fail: '  + str(e))
            