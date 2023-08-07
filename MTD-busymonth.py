#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime, json, calendar,os
from sharedutils import gcount, gcountYear, gcountMonth, last_day_of_month
from sharedutils import openjson, stdlog
from dotenv import load_dotenv  
from mastodon import Mastodon

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
image_filename = f'./docs/graphs/victims_per_day_{year}{month:02d}.png'
post_count = count_posts_by_month(year, month)

message = '🏴‍☠️💰 ' + calendar.month_name[month] + ' was another busy month for #Ransomware groups' 
message = message + '\n\n📈 https://Ransomware.live has tracked ' + str(post_count) + ' victims in ' + calendar.month_name[month] + ' ' + str(year) 
message = message + '\n\n🔗 More statistics available at https://www.ransomware.live/#/stats' + str(year) + '?id=' + calendar.month_name[month].lower() +'\n'

# Post the image to Mastodon
post_to_mastodon(image_filename,message)
