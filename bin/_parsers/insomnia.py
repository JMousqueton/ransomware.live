"""
    From Template v4 - 202412827
    +----------------------------------------------+
    | Description | Website | published | post URL |
    +-----------------------+-----------+----------+
    |       X     |    X    |           |     X    |
    +-----------------------+-----------+----------+
    Rappel : def appender(post_title, group_name, description="", website="", published="", post_url="", country="")
"""

import os,datetime,sys,re, json
from bs4 import BeautifulSoup
from datetime import datetime
from shared_utils import find_slug_by_md5, appender,extract_md5_from_filename, errlog
from pathlib import Path
from dotenv import load_dotenv
import pycountry

env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))

def main():
    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith('insomnia-'):
                html_doc=tmp_dir / filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs=soup.find_all('div', {"class": "book-card"})
                for article in divs:
                    # Extract the title
                    title_element = article.find('h3', class_='info-title')
                    if not title_element:
                        continue
                    title = title_element.text.strip()
                    title = title.replace('amp;','')

                    # Extract the URL
                    url_site = find_slug_by_md5('insomnia', extract_md5_from_filename(str(html_doc)))
                    url = title_element.a['href']
                    post_url = url_site + url

                    # Extract website from card-meta
                    try:
                        card_meta = article.find('div', class_='card-meta')
                        website_span = None
                        for span in card_meta.find_all('span'):
                            if 'Website:' in span.text:
                                website_span = span
                                break
                        if website_span:
                            website_text = website_span.text.replace('Website:', '').strip()
                            website = website_text if website_text else ''
                        else:
                            website = ''
                    except:
                        website = ''

                    # Extract description
                    try:
                        description = article.find('p', class_='info-desc').text.strip().replace('\n', ' ')
                        description = description.replace('amp;','')
                    except:
                        description = ''

                    # Extract location and convert country to 2-letter code
                    country = ''
                    try:
                        card_meta = article.find('div', class_='card-meta')
                        location_span = None
                        for span in card_meta.find_all('span'):
                            if 'Location:' in span.text:
                                location_span = span
                                break
                        if location_span:
                            location_text = location_span.text.replace('Location:', '').strip()
                            # Extract country from location (usually last part after comma)
                            location_parts = [part.strip() for part in location_text.split(',')]
                            country_name = location_parts[-1] if location_parts else ''

                            # Convert country name to 2-letter code using pycountry
                            if country_name:
                                try:
                                    # Try fuzzy search to handle variations
                                    country_obj = pycountry.countries.search_fuzzy(country_name)[0]
                                    country = country_obj.alpha_2
                                except:
                                    # If fuzzy search fails, keep original or empty
                                    country = ''
                    except:
                        country = ''

                    # Extract published date and convert to standard format
                    published = ''
                    try:
                        card_meta = article.find('div', class_='card-meta')
                        notified_span = None
                        for span in card_meta.find_all('span'):
                            if 'Notified:' in span.text:
                                notified_span = span
                                break
                        if notified_span:
                            date_str = notified_span.text.replace('Notified:', '').strip()
                            # Parse date in format "2026-1-23" and convert to "2026-02-07 20:22:08.507695"
                            try:
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                                published = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                            except:
                                # Try alternative format without leading zeros
                                try:
                                    parts = date_str.split('-')
                                    if len(parts) == 3:
                                        year, month, day = parts
                                        date_obj = datetime(int(year), int(month), int(day))
                                        published = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                                except:
                                    published = ''
                    except:
                        published = ''

                
                    """
                    print('victim:', title)
                    print('post_url:', post_url)
                    print('published:', published)
                    print('website:', website)
                    print('description:', description)
                    print('Country:', country)
                    print('-' * 40)
                    """
                    appender(title, 'insomnia', description, website, published, post_url, country)

                file.close()
        except:
            errlog('insomnia : ' + 'parsing fail')
