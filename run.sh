#!/usr/bin/bash

START_TIME=$(date +%s)
# Define the lock file path
LOCKFILE="/tmp/ransomwarelive.lock"
RL_HOME_DIR="/var/www/ransomware.live"
LOGFILE="/var/log/ransomwarelive.log" 

# Log the execution time to run.log
EXECUTION_DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Function to remove the lock file on exit
remove_lock() {
    rm -f "$LOCKFILE"
}

# Check if the lock file exists
if [ -e "$LOCKFILE" ]; then
    # Get the current time and the file creation time
    CURRENT_TIME=$(date +%s)
    FILE_CREATION_TIME=$(stat -c %Y "$LOCKFILE")
    
    # Calculate the time difference in seconds
    TIME_DIFF=$((CURRENT_TIME - FILE_CREATION_TIME))
    
    # Convert 3 hours to seconds (3 * 60 * 60)
    THREE_HOURS_IN_SECONDS=10800
    
    # Check if the time difference is greater than 3 hours
    if [ "$TIME_DIFF" -gt "$THREE_HOURS_IN_SECONDS" ]; then
        echo "Lock file is older than 3 hours. Please investigate."
        curl -s \
  --form-string "token=${PUSH_API}" \
  --form-string "user=${PUSH_USER}" \
  --form-string "message=ERROR: lock file older than 3 hours !!!" \
  https://api.pushover.net/1/messages.json > /dev/null
        exit 1
    else  
        echo "Script is already running. Exiting."
        exit 1
    fi
else
    # Create a lock file
    echo "Creating lock file : $LOCKFILE"
    touch "$LOCKFILE"
    # Ensure the lock file is removed when the script exits
    trap remove_lock EXIT
fi

service tor reload
## Go to directory 
cd ${RL_HOME_DIR}
## Delete older files
find ./source/ -maxdepth 1 -type f -mtime +1 -exec rm {} \;
## Load all env. variable 
source .env
## Scrape all ransomware group website 
SCRAPE_BEGIN_TIME=$(date +%s)
python3 ransomwatch.py scrape 
SCRAPE_END_TIME=$(date +%s)
SCRAPE_EXECUTION_TIME=$((SCRAPE_END_TIME - SCRAPE_BEGIN_TIME))

## Delete file less than 1k 
find ./source/  -maxdepth 1 -type f -size -1024c -exec rm {} \;
## Remove duplicate source (optimization)
python3 remove_duplicate.py
## Parse HTML file to find new victim
PARSE_BEGIN_TIME=$(date +%s)
python3 ransomwatch.py parse 
PARSE_END_TIME=$(date +%s)
PARSE_EXECUTION_TIME=$((PARSE_END_TIME - PARSE_BEGIN_TIME))

## Define Country from title, website, or description
python3 get-country.py 
## Check HudsonRock for infostealer 
python3 query_auto_hudsonrock.py

## Generate the website in markdown
MARKDOWN_BEGIN_TIME=$(date +%s)
python3 ransomwatch.py markdown
MARKDOWN_END_TIME=$(date +%s)
MARKDOWN_EXECUTION_TIME=$((MARKDOWN_END_TIME - MARKDOWN_BEGIN_TIME))

## Generate the RSS feed 
python3 generateRSS.py 
## Generate a RSS feed by ransomware group
python3 grouprss.py
## Generate sitemap.xml
python3 sitemap.py
## update Cartographie 
curl https://raw.githubusercontent.com/cert-orangecyberdefense/ransomware_map/main/OCD_WorldWatch_Ransomware-ecosystem-map.pdf -o ${RL_HOME_DIR}/docs/OCD_WorldWatch_Ransomware-ecosystem-map.pdf
## Update ransom_notes
cd ${RL_HOME_DIR}/docs/ransomware_notes
git fetch
# Check for any ransomware notes update
if git diff --quiet HEAD origin/main; then
  echo "No update."
else
  echo "Update available. Execute git pull..."
  git pull
  curl -s \
  --form-string "token=${PUSH_API}" \
  --form-string "user=${PUSH_USER}" \
  --form-string "message=New Ransom notes has been added" \
  https://api.pushover.net/1/messages.json > /dev/null
  cd ${RL_HOME_DIR}
  python3 ransom_notes.py
fi
cd ${RL_HOME_DIR}
./negotiation-update.sh
python3 create-negotiation.py
## Generate ransomware negotiation 
python3 negotiations.py 
## Generate recent attacks page 
python3 cyberattacks.py
python3 generateCyberAttacksRSS.py
## Search for new ransomware group
python3 DetectNewRansomware.py
#./assets/sources.zsh
## Generate ransomware Cloud 
python3 generateCloud.py
## Crypto information 
python3 addcrypto.py
## Crypt index
python3 ransom_crypto.py
## generation RSS feed for negotiation
python3 generateNegoRSS.py  
## Generate Countries
python3 countries.py 
## Generate graph top10 Countries 
python3 graph-country-year.py
## Generate worldmap
python3 worldmap.py
## Generate graph by Region
python3 graph_by_region.py
## Check PR for DarkFeedCTI
python3 check_PR_DeepDarkCTI.py

END_TIME=$(date +%s)
EXECUTION_TIME=$((END_TIME - START_TIME))

# Log the execution time to run.log
{
    echo "$EXECUTION_DATE,$SCRAPE_EXECUTION_TIME,$PARSE_EXECUTION_TIME,$MARKDOWN_EXECUTION_TIME,$EXECUTION_TIME"
} >> "$LOGFILE"

# Calculate minutes and seconds
MINUTES=$((EXECUTION_TIME / 60))
SECONDS=$((EXECUTION_TIME % 60))

echo "Execution time: $MINUTES minutes and $SECONDS seconds"

# Check if the execution time exceeds 90 minutes
if (( MINUTES > 100 )); then
  curl -s \
  --form-string "token=${PUSH_API}" \
  --form-string "user=${PUSH_USER}" \
  --form-string "message=WARNING: execution script longer than expected : ${MINUTES} minutes !!!" \
  https://api.pushover.net/1/messages.json > /dev/null
fi
python3 admin_exec_time.py
python3 generate_admin.py
