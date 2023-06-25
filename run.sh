#!/usr/bin/zsh
service tor reload
## Go to directory 
cd /var/www/ransomware.live/
## Load all env. variable 
source .env
## Scrape all ransomware group website 
python3 ransomwatchv2.py scrape 
## Parse HTML file to find new victim
python3 ransomwatchv2.py parse 
## Generate the RSS feed 
python3 generateRSS.py 
## Crypto information 
python3 addcrypto.py 
## Generate recent attacks page 
python3 recentcyberattacks.py 
## Generate graph for each ransomware group 
#python3 graphgroup.py
## Generate the website in markdown
python3 ransomwatchv2.py markdown
## Search for new ransomware group
./assets/sources.zsh
## Generate sitemap.xml
./assets/sitemap.sh
