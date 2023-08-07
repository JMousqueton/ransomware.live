#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime, json, calendar,os
import matplotlib.pyplot as plt
from sharedutils import gcount, gcountYear, gcountMonth, last_day_of_month
from sharedutils import openjson, stdlog
from dotenv import load_dotenv  
from mastodon import Mastodon

def topten_group_by_month(year,month):
    '''
    plot the number of posts by group in a barchart
    '''
    posts = openjson('posts.json')
    # group_counts = gcountYear(posts,year)
    group_counts = gcountMonth(posts,year,month)
    group_counts = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    # group_counts = [x for x in group_counts]
    groups = [x[0] for x in group_counts]
    counts = [x[1] for x in group_counts]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.bar(groups, counts, color="#42b983")
    plt.xlabel('Group Name\n© Ransomware.live')
    plt.xticks(rotation=90)
    plt.ylabel('# of Victims')
    plt.title('Top 10 active Groups in ' + calendar.month_name[month] + ' ' + str(year))

    # Adding value labels to the bars
    for i, count in enumerate(counts):
        plt.text(i, count, str(count), ha='center', va='bottom', fontsize=10, color='#42b983')
    
    image_filename = f'/tmp/toptenbygroup{year}{month:02d}.png'
    plt.savefig(image_filename, dpi=300, bbox_inches="tight", pad_inches=0.1, transparent=True)
    plt.clf()
    plt.cla()
    return image_filename

def post_to_mastodon(image_filename,message):
    mastodon = Mastodon(
        access_token=os.getenv('MASTODON_TOKEN'),
        api_base_url='https://infosec.exchange'
    )
    
    media = [mastodon.media_post(image_filename)]

    mastodon.status_post(status=message, media_ids=media)

def count_posts_by_month(year, month):
    count = 0
    posts = openjson('posts.json')
    for post in posts:
        post_date = datetime.datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f')
        if post_date.year == year and post_date.month == month:
            count += 1
    return count


if __name__ == "__main__":
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
     /  ************  \   ransomware.live     /  ************  \ 
    --------------------                    --------------------
    '''
    )
    stdlog('Generating Top 10 Most activie Groups by victims for previous month')

# Load environment variables from .env file
load_dotenv()

# Get the current year and month
year = datetime.datetime.now().year
month = datetime.datetime.now().month

# Calculate the previous month's value and year
month = month - 1
if month == 0: 
   year = year - 1 

# Call the function with the previous month of the current year
image_filename = topten_group_by_month(year, month)
post_count = count_posts_by_month(year, month)

message = '🏴‍☠️💰Check out the top 10 #Ransomware active groups for ' + calendar.month_name[month] + ' ' + str(year) 
message = message + '\n\n📈 Ransomware.live has tracked ' + str(post_count) + ' victims in ' + calendar.month_name[month] + ' ' + str(year) 
message = message + '\n\n🔗 More statistics : https://www.ransomware.live/#/stats' + str(year) + '?id=' + calendar.month_name[month].lower() +'\n'

# Post the image to Mastodon
post_to_mastodon(image_filename,message)
