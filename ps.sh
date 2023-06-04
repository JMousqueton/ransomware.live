#!/bin/bash
##
# check what is going on ;)
##
if ps -ef | grep -q "[s]crape\|[p]arse\|[m]arkdown"; then
  process_name=$(ps -ef | grep -o '[s]crape\|[p]arse\|[m]arkdown')
  elapsed_seconds=$(ps -p $(pgrep -f "python3 ransomwatch.py $process_name") -o etimes= | awk '{print $1}')
  elapsed_minutes=$((elapsed_seconds/60))
  bold=$(tput bold)
  reset=$(tput sgr0)
  echo "The ${bold}$process_name${reset} process is running since ${bold}$elapsed_minutes${reset} minutes"
  if [[ $process_name == "scrape" ]]; then 
	gang=$(ls -tr ./source/  |  tail -n 1 | cut -d '-' -f 1)
	echo "	Processing $(tput bold)$gang$(tput sgr0)'s website"	
 fi
else
	echo " (!) None of the ${bold}Ransomware.live ${reset}processes are running"
fi
