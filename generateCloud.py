#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Generate Ransomware Gang's Cloud image based on number of victims for Ransomware.live 
By Julien Mousqueton 
'''
import json,sys,os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs'))) 
from ransomwarelive import stdlog, errlog, openjson, add_watermark


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

try:
# Read the JSON data from posts.json
    data = openjson('./data/victims.json')
except:
    errlog('Ransomware Cloud: Error reading posts.json')

# Filter the posts for the year 2023
data = [post for post in data if 'discovered' in post and post['discovered'].startswith('2023')]

# Extract the group_name values from each post
group_names = [post.get('group_name', '') for post in data]

# Preprocess the group_names list to replace 'lockbit3' and 'lockbit2' with 'lockbit'
group_names = [name.replace('lockbit3', 'lockbit').replace('lockbit2', 'lockbit') for name in group_names]

# Count the occurrences of each word in the preprocessed group_names list
word_counts = Counter(group_names)

# Set the custom color map (you can choose any available colormap)
# could be 'viridis', 'plasma', 'magma', 'inferno', 'cividis
custom_color_map = 'viridis'

# Generate the word cloud with word frequencies and customized color 
wordcloud = WordCloud(width=1200, height=400, background_color="white", colormap=custom_color_map).generate_from_frequencies(word_counts)

try:
    # Save the word cloud image to docs/ransomwarecloud.png
    output_path = "docs/ransomwarecloud.png"
    wordcloud.to_file(output_path)
    stdlog("Ransomware Cloud : image saved successfully!")
    add_watermark(output_path)
except:
    errlog("Ransomware Cloud : Error while saving image")
