#!/bin/bash
##
# Check what is going on ;)
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
    processes+=("$process_name:$process_id:$elapsed_minutes")
  fi
done < <(ps -ef | grep ransomwatch | grep -E "[s]crape|[p]arse|[m]arkdown")

# Check if any relevant processes were found
if [ "${#processes[@]}" -gt 0 ]; then
  bold=$(tput bold)
  reset=$(tput sgr0)

  # Iterate through the array and display process information
  for process_info in "${processes[@]}"; do
    IFS=':' read -r process_name process_id elapsed_minutes <<< "$process_info"

    if [[ $process_name == "parse" ]]; then
      # Execute lsof for the parse process and grep for html files
      lsof_output=$(lsof -p "$process_id" | grep html)
      if [[ -n $lsof_output ]]; then
        group_name=$(echo "$lsof_output" | awk -F'source/' '{print $2}' | awk -F'-' '{print $1}')
        echo "The ${bold}$process_name${reset} process (PID: $process_id) is running since ${bold}$elapsed_minutes${reset} minutes with group: ${bold}$group_name${reset}"
      else
        echo "The ${bold}$process_name${reset} process (PID: $process_id) is running since ${bold}$elapsed_minutes${reset} minutes, but no HTML files are currently open."
      fi
    else
         echo "The ${bold}$process_name${reset} process (PID: $process_id) is running since ${bold}$elapsed_minutes${reset} minutes"
         if [[ $process_name == "scrape" ]]; then
            latest_file=$(ls -tr ./source/ | tail -n 1 | cut -d '-' -f 1)
            echo "  Last processed gang : $(tput bold)$latest_file$(tput sgr0)"
         fi
      fi
  done
else
  echo " (!) None of the ${bold}Ransomware.live ${reset}processes are running"
fi
