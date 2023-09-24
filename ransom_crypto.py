import os
import shutil
import json
from datetime import datetime as dt 

NowTime=dt.now()


print(
    '''
       _______________                        |*\_/*|________
      |  ___________  |                      ||_/-\_|______  |
      | |           | |                      | |           | |
      | |   0   0   | |                      | |   0   0   | |
      | |     -     | |                      | |     -     | |
      | |   \___/   | |                      | |   \___/   | |
      | |___     ___| |                      | |___________| |
      |_____|\_/|_____|                      |_______________|
        _|__|/ \|_|_.............💔.............._|________|_
       / ********** \                          / ********** \ 
     /  ************  \     ransomwhat?      /  ************  \ 
    --------------------                    --------------------
    '''
)

source_dir = './docs/crypto'

# Get a list of all directories in the specified directory, excluding .git
directories = [f for f in os.listdir(source_dir) if f.endswith('.md')]

# Sort the directories alphabetically
directories = sorted(directories, key=lambda x: x.lower())

header = "\n"
header += "# 💰 Crypto wallet(s)  by groups"
header += "\n\n"
header += "> [!INFO]"
header += "> Ransomware crypto wallets are provided by [Ransomwhere](https://ransomwhe.re/)\n"
header += "> \n"
header += "\n\n"
# Prepare the Markdown table header
header += "| | | | | |\n"  # Empty header row
header += "|:------------:|:------------:|:------------:|:------------:|:------------:|\n"  # Table formatting

# Prepare the Markdown table rows
rows = ""
for i in range(0, len(directories), 5):
    row = "|"
    for j in range(5):
        if i + j < len(directories):
            row += f" [{directories[i + j].replace('.md','')}](crypto/{directories[i + j]})|"
        else:
            row += "            |"
    rows += row + "\n"

# Generate the Markdown file content
markdown_content = f"{header}{rows}"

# Write the content to a file
output_file = "./docs/crypto.md"
with open(output_file, "w") as file:
    file.write(markdown_content)
    file.write('\n\nLast update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_\n\n')


print(f"Ransom wallet index file generated successfully.")

