#!/bin/bash
RL_HOME_DIR="/var/www/ransomware-ng"
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
fi
cd ${RL_HOME_DIR}
