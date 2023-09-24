#!/bin/bash
##
# check what is going on ;)
##

# Initialize an array to store process information
declare -a processes

# Find all relevant processes and store their information in the array
while read -r process_info; do
  process_name=$(echo "$process_info" | awk '{print $10}')
  process_id=$(echo "$process_info" | awk '{print $2}')
  elapsed_seconds=$(ps -p "$process_id" -o etimes= | awk '{print $1}')
  elapsed_minutes=$((elapsed_seconds / 60))
  
  if [[ $process_name == "scrape" || $process_name == "parse" || $process_name == "markdown" ]]; then
    processes+=("$process_name:$elapsed_minutes")
  fi
done < <(ps -ef | grep ransomwatch | grep -E "[s]crape|[p]arse|[m]arkdown")

# Check if any relevant processes were found
if [ "${#processes[@]}" -gt 0 ]; then
  bold=$(tput bold)
  reset=$(tput sgr0)

  # Iterate through the array and display process information
  for process_info in "${processes[@]}"; do
    process_name="${process_info%%:*}"
    elapsed_minutes="${process_info#*:}"

    echo "The ${bold}$process_name${reset} process is running since ${bold}$elapsed_minutes${reset} minutes"
    
    if [[ $process_name == "scrape" ]]; then 
      latest_file=$(ls -tr ./source/ | tail -n 1 | cut -d '-' -f 1)
      echo "  Last processed gang : $(tput bold)$latest_file$(tput sgr0)"
    fi
  done
else
  echo " (!) None of the ${bold}Ransomware.live ${reset}processes are running"
fi
