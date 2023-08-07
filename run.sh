#!/usr/bin/zsh
service tor reload
## Go to directory 
cd /var/www/ransomware.live/
## Load all env. variable 
source .env
## Scrape all ransomware group website 
python3 ransomwatch.py scrape 
## Parse HTML file to find new victim
python3 ransomwatch.py parse 
## Generate the RSS feed 
python3 generateRSS.py 
## Generate ransomware Cloud 
python3 generateCloud.py
## Crypto information 
python3 addcrypto.py
## Generate the website in markdown
python3 ransomwatch.py markdown
## Generate recent attacks page 
python3 cyberattacks.py
## Generate graph for each ransomware group 
#python3 graphgroup.py
## Generate ransomware negotiation 
python3 negotiations.py 
## Search for new ransomware group
./assets/sources.zsh
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

