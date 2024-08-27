#!/bin/bash

# Bash Completion Script for ransomcmd.py
# ----------------------------------------
# This script provides command-line tab completion for the ransomcmd.py tool.
# It includes subcommands and options based on the functionality provided by the tool.
# To use this script, save it to your home directory and source it from your .bashrc file.
#
# Instructions:
# 1. Install bash_completion
#           sudo apt-get install bash-completion
# 2. Add `source ransomcmd_completion.sh` to your ~/.bashrc file.
# 3. Reload your bash configuration using `source ~/.bashrc`.
# 4. Navigate to the directory containing ransomcmd.py and test the completion by typing:
#    `./ransomcmd.py [Tab]`
#
# ----------------------------------------


_ransomcmd_completions()
{
    local cur prev subcommands opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Define the subcommands based on the list provided
    subcommands="scrape parse generate screenshot status search rss infostealer tools add append"

    # Global options
    global_opts="--help --version"

    # Complete subcommands when typing the main command
    if [[ ${COMP_CWORD} == 1 ]]; then
        COMPREPLY=( $(compgen -W "${subcommands} ${global_opts}" -- ${cur}) )
        return 0
    fi

    # Customize completion based on the subcommand
    case "${prev}" in
        scrape)
            opts="--group"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        parse)
            opts="--group"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        generate)
            opts=""
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        screenshot)
            opts="--group  --url"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        status)
            opts=""
            COMPREPLY=()
            return 0
            ;;
        search)
            opts="--victim"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        rss)
            opts=""
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        infostealer)
            opts="--domain"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        tools)
            opts="duplicate order blur"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        blur)
            opts="--file"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        add)
            opts="--name --location"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        append)
            opts="--name --location"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
    esac
}

complete -F _ransomcmd_completions ./ransomcmd.py

