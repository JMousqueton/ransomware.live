#!/usr/bin/zsh
service tor reload
## Go to directory 
cd /var/www/ransomware.live/
## Delete older files
find ./source/ -maxdepth 1 -type f -mmin +90 -exec rm {} \;
## Load all env. variable 
source .env
## Scrape all ransomware group website 
python3 ransomwatch.py scrape 
## Delete file less than 1k 
#find ./source/  -maxdepth 1 -type f -size -1024c -exec rm {} \;
## bypass error on ransomed
###service tor reload
###python3 scrapegang.py ransomed 
## Reload service tor 
service tor reload
## Parse HTML file to find new victim
python3 ransomwatch.py parse 
## Generate the RSS feed 
python3 generateRSS.py 
## Generate a RSS feed by ransomware group
python3 grouprss.py
## Define Country from title, website, or description
python3 get-country.py 
## Generate the website in markdown
python3 ransomwatch.py markdown
## Generate sitemap.xml
python3 sitemap.py
# update Cartographie 
curl https://raw.githubusercontent.com/cert-orangecyberdefense/ransomware_map/main/OCD_WorldWatch_Ransomware-ecosystem-map.pdf -o docs/OCD_WorldWatch_Ransomware-ecosystem-map.pdf
# Update ransom_notes
cd docs/ransomware_notes
git fetch
# Vérifier s'il y a des mises à jour
if git diff --quiet HEAD origin/main; then
  echo "Aucune mise à jour disponible."
else
  echo "Mise à jour détectée. Exécution de git pull..."
   curl -s \
  --form-string "token=${PUSH_API}" \
  --form-string "user=${PUSH_USER}" \
  --form-string "message=New Ransom notes has been added" \
  https://api.pushover.net/1/messages.json > /dev/null
  git pull
  cd -
  python3 ransom_notes.py
fi
cd /var/www/ransomware.live/
## Generate ransomware negotiation 
python3 negotiations.py 
## Generate recent attacks page 
python3 cyberattacks.py
python3 generateCyberAttacksRSS.py
## Search for new ransomware group
python3 DetectNewRansomware.py
./assets/sources.zsh
## Generate ransomware Cloud 
python3 generateCloud.py
## Crypto information 
python3 addcrypto.py
## Crypt index
python3 ransom_crypto.py
# Update negotiation chat
negotiation-update.sh
python3 generateNegoRSS.py  
## Generate Countries
python3 countries.py 
## Generate graph top10 Countries 
python3 graph-country-year.py
