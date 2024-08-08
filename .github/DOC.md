
# Ransomware.live

Teh ransomcmd.py is a comprehensive command-line tool designed to manage and monitor ransomware activities. It supports various functionalities including scraping ransomware DLS (Dark Leak Sites), parsing the collected data, generating reports and graphs, taking screenshots of ransomware sites, and more. The program is built with extensibility in mind, allowing for easy addition of new features and integration with existing tools and libraries.

## Table of Contents

- [Usage](#usage)
- [Dependencies](#dependencies)
- [Environment Variables](#environment-variables)
- [Author](#author)
- [Version](#version)
- [Commands](#commands)
  - [scrape](#scrape)
  - [parse](#parse)
  - [generate](#generate)
  - [screenshot](#screenshot)
  - [status](#status)
  - [search](#search)
  - [rss](#rss)
  - [infostealer](#infostealer)
  - [tools](#tools)
    - [duplicate](#duplicate)
    - [order](#order)
    - [blur](#blur)
  - [add](#add)
  - [append](#append)

## Usage

\`\`\`bash
python3 ransomcmd.py <command> [options]
\`\`\`

## Dependencies

- Python 3.x
- Python packages: sys, os, asyncio, argparse, dotenv, hashlib, time, importlib, glob, datetime, atexit, tempfile, subprocess, re

## Environment Variables

Managed via a `.env` file, which includes configurations for directories, data files, etc.

## Author

Julien Mousqueton

## Commands

### scrape

Scrape ransomware DLS sites.

\`\`\`bash
python3 ransomcmd.py scrape [options]
\`\`\`

Options:

- `-F`, `--force`: Force scraping
- `-g`, `--group`: Specify a specific group to scrape

### parse

Parse ransomware DLS sites.

\`\`\`bash
python3 ransomcmd.py parse [options]
\`\`\`

Options:

- `-g`, `--group`: Specify a specific group to parse

### generate

Generate Ransomware.live site.

\`\`\`bash
python3 ransomcmd.py generate
\`\`\`

### screenshot

Generate screenshot for ransomware sites.

\`\`\`bash
python3 ransomcmd.py screenshot [options]
\`\`\`

Options:

- `-g`, `--group`: Specify a specific group to screenshot
- `-u`, `--url`: Specify a specific URL to screenshot

### status

Show the status of ransomware.live.

\`\`\`bash
python3 ransomcmd.py status
\`\`\`

### search

Search victim in the database.

\`\`\`bash
python3 ransomcmd.py search [options]
\`\`\`

Options:

- `-v`, `--victim`: Specify a victim name
- `-d`, `--domain`: Specify a domain name

### rss

Generate RSS feeds.

\`\`\`bash
python3 ransomcmd.py rss
\`\`\`

### infostealer

Query Hudsonrock database.

\`\`\`bash
python3 ransomcmd.py infostealer [options]
\`\`\`

Options:

- `-d`, `--domain`: Specify a victim domain

### tools

Tools for Ransomware.live.

\`\`\`bash
python3 ransomcmd.py tools <tool_command> [options]
\`\`\`

#### duplicate

Remove duplicate source files.

\`\`\`bash
python3 ransomcmd.py tools duplicate
\`\`\`

#### order

Order groups by alphabetic order.

\`\`\`bash
python3 ransomcmd.py tools order
\`\`\`

#### blur

Blur a picture.

\`\`\`bash
python3 ransomcmd.py tools blur [options]
\`\`\`

Options:

- `-f`, `--file`: Full path of the image to blur

### add

Add a new ransomware group.

\`\`\`bash
python3 ransomcmd.py add [options]
\`\`\`

Options:

- `-n`, `--name`: Specify the ransomware group name
- `-l`, `--location`: Specify the ransomware group site

### append

Add a new ransomware site to an existing group.

\`\`\`bash
python3 ransomcmd.py append [options]
\`\`\`

Options:

- `-n`, `--name`: Specify the ransomware group name
- `-l`, `--location`: Specify the ransomware group site
