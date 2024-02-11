import os
import shutil
import json
from datetime import datetime as dt 

NowTime=dt.now()

source_dir = './docs/ransomware_notes'
target_dir = './docs/notes'

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

with open('groups.json', 'r') as groupsjson:
    # Load the JSON data
    data = json.load(groupsjson)


# Iterate over the subdirectories in the source directory
for subdir in os.listdir(source_dir):
    subdir_path = os.path.join(source_dir, subdir)
    
    # Check if it is a directory
    if os.path.isdir(subdir_path):
        # Create a file with the name of the subdirectory in the target directory
        file_path = os.path.join(target_dir, subdir + '.md')
        
        # Open the file in write mode and write the name of the directory
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('# 💰 _Ransom notes for group_ '+ subdir + '\n')
            for group in data:
                if subdir.lower() in group['name']:
                    file.write('> 🔗 ['+ subdir + '](group/' + subdir.lower() + ')\n')
        
            header = "\n\n"
            header += "> [!TIP]"
            header += "> Ransomware notes are provided by [Zscaler ThreatLabz](https://github.com/threatlabz/ransomware_notes) under MIT License\n"
            header += "> \n"
            header += "\n\n"

        # Iterate over the files in the subdirectory
        for filename in os.listdir(subdir_path):
            file_path_source = os.path.join(subdir_path, filename)
            
            # Check if it is a file
            if os.path.isfile(file_path_source):
                # Append the content of each file to the corresponding target file
                with open(file_path_source, 'r', encoding='latin-1') as source_file:
                    content = source_file.read()
                
                with open(file_path, 'a', encoding='utf-8') as target_file:
                    target_file.write('* **[' +  os.path.basename(file_path_source) + '](https://ransomware.live/ransomware_notes/' + subdir + '/' + os.path.basename(file_path_source).replace(' ','%20') + ')**\n')
                    target_file.write('\n```\n')
                    target_file.write(content)
                    target_file.write('\n```\n')
        with open(file_path, 'a', encoding='utf-8') as target_file:
            target_file.write(header)
            target_file.write('\n\nLast update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_\n\n')

# Get a list of all directories in the specified directory, excluding .git
directories = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d)) and d != ".git"]

# Sort the directories alphabetically
directories = sorted(directories, key=lambda x: x.lower())

header = "\n"
header += "# 💰 All ransomware notes by groups"
header += "\n\n"
header += "> [!INFO]"
header += "> Ransomware notes are provided by [Zscaler ThreatLabz](https://github.com/threatlabz/ransomware_notes) under MIT License\n"
header += "> \n"
header += "\n\n"
# Prepare the Markdown table header
header += "| | | | | | | | | | |\n"  # Empty header row
header += "|:------------:|:------------:|:------------:|:------------:|:------------:|:------------:|:------------:|:------------:|:------------:|:------------:|\n"  # Table formatting

# Prepare the Markdown table rows
rows = ""
for i in range(0, len(directories), 10):
    row = "|"
    for j in range(10):
        if i + j < len(directories):
            row += f" [{directories[i + j]}](notes/{directories[i + j]})|"
        else:
            row += "            |"
    rows += row + "\n"

# Generate the Markdown file content
markdown_content = f"{header}{rows}"

# Write the content to a file
output_file = "./docs/ransomnotes.md"
with open(output_file, "w") as file:
    file.write(markdown_content)
    file.write('\n\nLast update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_\n\n')


print(f"Ransom Notes index file generated successfully.")

