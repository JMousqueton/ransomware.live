#!/bin/bash

if [[ "$1" != "groups" && "$1" != "posts" ]]
then
    echo "Invalid parameter. Please specify either 'groups' or 'posts'."
    exit 1
fi

if [[ "$1" == "posts" ]] 
then 
	action="parse"
else 
	action="scrape"
fi

if pgrep -f "python3 ransomwatch.py $action" > /dev/null
then
    echo "(!) unable to edit $1"
else
    vi $1.json 
fi
