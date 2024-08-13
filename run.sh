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
    
    # Convert 2 hours to seconds (2 * 60 * 60)
    THREE_HOURS_IN_SECONDS=7200
    
    # Check if the time difference is greater than 3 hours
    if [ "$TIME_DIFF" -gt "$THREE_HOURS_IN_SECONDS" ]; then
        echo "Lock file is older than 2 hours. Please investigate."
        # Check if PUSH_USER is set
        if [ -z "$PUSH_USER" ]; then
            echo "PUSH_USER is not set. Cannot send notification. Exiting."
            exit 1
        fi
        curl -s \
  --form-string "token=${PUSH_API}" \
  --form-string "user=${PUSH_USER}" \
  --form-string "message=ERROR: lock file older than 2 hours !!!" \
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

### Go 
## Update ransom_notes
cd ${RL_HOME_DIR}/docs/ransomware_notes
git fetch
# Check for any ransomware notes update
if git diff --quiet HEAD origin/main; then
  echo "No update."
else
    if [ -z "$PUSH_USER" ]; then
        echo "PUSH_USER is not set. Cannot send notification. Exiting."
    else 
        echo "Update available. Execute git pull..."
        git pull
        curl -s \
            --form-string "token=${PUSH_API}" \
            --form-string "user=${PUSH_USER}" \
            --form-string "message=New Ransom notes has been added" \
            https://api.pushover.net/1/messages.json > /dev/null
    fi
fi
cd ${RL_HOME_DIR}

## Download carto pdf 
curl https://raw.githubusercontent.com/cert-orangecyberdefense/ransomware_map/main/OCD_WorldWatch_Ransomware-ecosystem-map.pdf -o ${RL_HOME_DIR}/docs/OCD_WorldWatch_Ransomware-ecosystem-map.pdf

cd ./import
git fetch
# Vérifier s'il y a des mises à jour
if git diff --quiet HEAD origin/main; then
    echo "Aucune mise à jour disponible."
else
    echo "Mise à jour détectée. Exécution de git pull..."
    git pull
    # Exécuter le script Python s'il y a eu une mise à jour
    if [ $? -eq 0 ]; then
        echo "Exécution de la mise à jour ..."
        cd ..
        if [ -z "$PUSH_USER" ]; then
            curl -s \
            --form-string "token=${PUSH_API}" \
            --form-string "user=${PUSH_USER}" \
            --form-string "message=New Ransoms chats have been added" \
            https://api.pushover.net/1/messages.json > /dev/null
        fi
    else
        echo "Erreur lors de la mise à jour du référentiel."
    fi
fi

cd ${RL_HOME_DIR}
SCRAPE_BEGIN_TIME=$(date +%s)
python3 ransomcmd.py scrape
SCRAPE_END_TIME=$(date +%s)
SCRAPE_EXECUTION_TIME=$((SCRAPE_END_TIME - SCRAPE_BEGIN_TIME))


PARSE_BEGIN_TIME=$(date +%s)
python3 ransomcmd.py parse
PARSE_END_TIME=$(date +%s)
PARSE_EXECUTION_TIME=$((PARSE_END_TIME - PARSE_BEGIN_TIME))


MARKDOWN_BEGIN_TIME=$(date +%s)
# TODO: Need to be include in ransomwarelive library --> generatesite 
python3 generatecyberattacks.py
python3 ransomcmd.py generate
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
if (( MINUTES > 90 )); then
    if [ -z "$PUSH_USER" ]; then
        echo "PUSH_USER is not set. Cannot send notification."
        exit 1
    fi
    curl -s \
  --form-string "token=${PUSH_API}" \
  --form-string "user=${PUSH_USER}" \
  --form-string "message=WARNING: execution script longer than expected : ${MINUTES} minutes !!!" \
  https://api.pushover.net/1/messages.json > /dev/null
fi
