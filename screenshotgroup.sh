#!/usr/bin/zsh
cd /var/www/ransomware.live/
for GROUP in $(jq '.[].name' groups.json | tr -d \")
do 
	python3 screenshotblog.py ${GROUP}
done
