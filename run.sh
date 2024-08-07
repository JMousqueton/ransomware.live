#!/usr/bin/bash
START_TIME=$(date +%s)
# Define the lock file path
LOCKFILE="/tmp/ransomwarelive.lock"
RL_HOME_DIR="/var/www/ransomware-ng"
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

./update_carto.sh
./update_negotiation.sh
./update_ransomnote.sh


SCRAPE_BEGIN_TIME=$(date +%s)
python3 ransomwarelive.py scrape
SCRAPE_END_TIME=$(date +%s)
SCRAPE_EXECUTION_TIME=$((SCRAPE_END_TIME - SCRAPE_BEGIN_TIME))


PARSE_BEGIN_TIME=$(date +%s)
python3 ransomwarelive.py parse
PARSE_END_TIME=$(date +%s)
PARSE_EXECUTION_TIME=$((PARSE_END_TIME - PARSE_BEGIN_TIME))


MARKDOWN_BEGIN_TIME=$(date +%s)
python3 ransomwarelive.py generate
python3 generateNegoRSS.py 
python3 generateworldmap.py
python3 generatecyberattacks.py
python3 generateCyberAttacksRSS.py 
python3 generatecountries.py
python3 generateCloud.py 
MARKDOWN_END_TIME=$(date +%s)
MARKDOWN_EXECUTION_TIME=$((MARKDOWN_END_TIME - MARKDOWN_BEGIN_TIME))

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
if (( MINUTES > 120 )); then
  curl -s \
  --form-string "token=${PUSH_API}" \
  --form-string "user=${PUSH_USER}" \
  --form-string "message=WARNING: execution script longer than expected : ${MINUTES} minutes !!!" \
  https://api.pushover.net/1/messages.json > /dev/null
fi
