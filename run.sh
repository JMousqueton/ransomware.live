#!/usr/bin/zsh
cd /var/www/ransomware.live/
source .env
python3 ransomwatch.py scrape 
python3 ransomwatch.py parse 
python3 generateRSS.py 
python3 ransomwatch.py markdown
python3 addcrypto.py 
python3 recentcyberattacks.py
python3 graphgroup.py
./assets/sources.zsh
./assets/sitemap.sh
