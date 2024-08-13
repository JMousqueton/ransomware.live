# -*- coding: utf-8 -*-
import datetime, json, calendar
import matplotlib.pyplot as plt
#from datetime import datetime
import sys,os
from dotenv import load_dotenv 
from datetime import datetime, timedelta
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import folium
import seaborn as sns

from mypycountries import get_coordinates, get_country_name # https://github.com/JMousqueton/MyPyCountries 

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from ransomwarelive import add_watermark, openjson, errlog, stdlog

env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)

DATA_DIR = os.getenv('DATA_DIR')
GROUPS_FILE = os.getenv('GROUPS_FILE')
VICTIMS_FILE = os.getenv('VICTIMS_FILE')
## 
GROUPS_FILE = DATA_DIR + GROUPS_FILE
VICTIMS_FILE = DATA_DIR + VICTIMS_FILE


## INTERNAL 

def gcount(posts):
    group_counts = {}
    for post in posts:
        if post['group_name'] in group_counts:
            group_counts[post['group_name']] += 1
        else:
            group_counts[post['group_name']] = 1
    return group_counts

def gcountYear(posts,year):
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    date_debut = datetime(year, 1, 1)
    date_fin = datetime(year, 12, 31)
    group_counts = {}
    for post in posts:
        if post['group_name'] in group_counts:
            date = datetime.strptime(post['discovered'], date_format)
            if date <= date_fin and date >= date_debut:
                group_counts[post['group_name']] += 1
        else:
            date = datetime.strptime(post['discovered'], date_format)
            if date <= date_fin and date >= date_debut:
                group_counts[post['group_name']] = 1
    return group_counts

def last_day_of_month(month, year):
    # Obtenir le dernier jour du mois en utilisant la fonction monthrange de la bibliothèque calendar
    last_day = calendar.monthrange(year, month)[1]
    return last_day

def gcountMonth(posts,year,month=0):
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    if month == 0:
        date_debut = datetime(year, 1, 1)
        date_fin = datetime(year, 12, 31)
    else: 
        date_debut = datetime(year, month, 1)
        date_fin = datetime(year, month, last_day_of_month(month,year))
    group_counts = {}
    for post in posts:
        if post['group_name'] in group_counts:
            date = datetime.strptime(post['published'], date_format)
            if date <= date_fin and date >= date_debut:
                group_counts[post['group_name']] += 1
        else:
            date = datetime.strptime(post['published'], date_format)
            if date <= date_fin and date >= date_debut:
                group_counts[post['group_name']] = 1
    return group_counts


###


def plot_posts_by_group():
    '''
    plot the number of posts by group in a barchart
    '''
    posts = openjson(VICTIMS_FILE)
    group_counts = gcount(posts)
    group_counts = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
    group_counts = [x for x in group_counts if x[0] != 'clop']
    groups = [x[0] for x in group_counts]
    counts = [x[1] for x in group_counts]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.bar(groups, counts, color="#42b983")
    plt.title('posts by group')
    plt.xlabel('group name')
    plt.xticks(rotation=90)
    plt.ylabel('# of posts')
    plt.savefig('docs/graphs/postsbygroup.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()


def plot_posts_by_group_by_year(year):
    '''
    plot the number of posts by group in a barchart
    '''
    posts = openjson(VICTIMS_FILE)
    group_counts = gcountYear(posts,year)
    group_counts = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
    group_counts = [x for x in group_counts]
    groups = [x[0] for x in group_counts]
    counts = [x[1] for x in group_counts]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.bar(groups, counts, color="#42b983")
    plt.title('Victims by group in ' + str(year))
    plt.xlabel('Group Name\n© Ransomware.live')
    plt.xticks(rotation=90)
    plt.ylabel('# of posts')
    plt.savefig('docs/graphs/postsbygroup'+str(year)+'.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()


def plot_posts_by_group_past_7_days():
    '''
    plot the number of posts by group over the last week in a barchart
    '''
    posts = openjson(VICTIMS_FILE) 
    seven_days_ago = datetime.now() - timedelta(days=7)
    posts = [post for post in posts if post['published'] >= seven_days_ago.strftime('%Y-%m-%d')]
    group_counts = gcount(posts)
    group_counts = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
    group_counts = [x for x in group_counts if x[0] != 'clop']
    groups = [x[0] for x in group_counts]
    counts = [x[1] for x in group_counts]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.bar(groups, counts, color="#42b983")
    plt.title('Victims by group last 7 days')
    plt.xlabel('Group name\n© Ransomware.live')
    plt.xticks(rotation=90)
    plt.ylabel('# of posts')
    plt.savefig('docs/graphs/postsbygroup7days.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def trend_posts_per_day():
    '''
    plot the trend of the number of posts per day
    '''
    posts = openjson(VICTIMS_FILE)
    dates = []
    for post in posts:
        dates.append(post['published'][0:10])
    # list of duplicate dates should be marged to show a count of posts per day
    # i.e ['2021-12-07', '2021-12-07', '2021-12-07', '2021-12-07', '2021-12-07']
    # becomes [{'2021-12-07',4}] etc
    datecount = {}
    for date in dates:
        if date in datecount:
            datecount[date] += 1
        else:
            datecount[date] = 1
    # remove '2021-09-09' - generic date of import along w/ anything before 2021-08
    datecount.pop('2021-09-09', None)
    datecount = {k: v for k, v in datecount.items() if k >= '2021-08-01'}
    datecount = list(datecount.items())
    datecount.sort(key=lambda x: x[0])
    dates = [datetime.strptime(x[0], '%Y-%m-%d').date() for x in datecount]
    counts = [x[1] for x in datecount]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.plot(dates, counts, color="#42b983")
    plt.title('Victims per day')
    plt.xlabel('Date\n© Ransomware.live')
    plt.xticks(rotation=90)
    plt.ylabel('# of posts')
    plt.savefig('docs/graphs/postsbyday.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()


def trend_posts_per_day_2022():
    '''
    plot the trend of the number of posts per day
    '''
    posts = openjson(VICTIMS_FILE)
    dates = []
    for post in posts:
        dates.append(post['published'][0:10])
    # list of duplicate dates should be marged to show a count of posts per day
    # i.e ['2021-12-07', '2021-12-07', '2021-12-07', '2021-12-07', '2021-12-07']
    # becomes [{'2021-12-07',4}] etc
    datecount = {}
    for date in dates:
        if date in datecount:
            datecount[date] += 1
        else:
            datecount[date] = 1
    # remove '2021-09-09' - generic date of import along w/ anything before 2021-08
    datecount.pop('2021-09-09', None)
    datecount = {k: v for k, v in datecount.items() if k >= '2022-01-01' and k <='2022-12-31'}
    datecount = list(datecount.items())
    datecount.sort(key=lambda x: x[0])
    dates = [datetime.strptime(x[0], '%Y-%m-%d').date() for x in datecount]
    counts = [x[1] for x in datecount]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.plot(dates, counts, color="#42b983")
    plt.title('Victims per day in 2022')
    plt.xlabel('Date\n© Ransomware.live')
    plt.xticks(rotation=90)
    plt.ylabel('# of posts')
    plt.savefig('docs/graphs/postsbyday2022.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def trend_posts_per_day_2023():
    '''
    plot the trend of the number of posts per day
    '''
    posts = openjson(VICTIMS_FILE)
    dates = []
    for post in posts:
        dates.append(post['published'][0:10])
    # list of duplicate dates should be marged to show a count of posts per day
    # i.e ['2021-12-07', '2021-12-07', '2021-12-07', '2021-12-07', '2021-12-07']
    # becomes [{'2021-12-07',4}] etc
    datecount = {}
    for date in dates:
        if date in datecount:
            datecount[date] += 1
        else:
            datecount[date] = 1
    # remove '2021-09-09' - generic date of import along w/ anything before 2021-08
    datecount = {k: v for k, v in datecount.items() if k >= '2023-01-01' and k <='2023-12-31'}
    datecount = list(datecount.items())
    datecount.sort(key=lambda x: x[0])
    dates = [datetime.strptime(x[0], '%Y-%m-%d').date() for x in datecount]
    counts = [x[1] for x in datecount]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.plot(dates, counts, color="#42b983")
    plt.title('Victims per day in 2023\n© Ransomware.live')
    plt.xlabel('date')
    plt.xticks(rotation=90)
    plt.ylabel('# of posts')
    plt.savefig('docs/graphs/postsbyday2023.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def trend_posts_per_day_2024():
    '''
    plot the trend of the number of posts per day
    '''
    posts = openjson(VICTIMS_FILE)
    dates = []
    for post in posts:
        dates.append(post['published'][0:10])
    # list of duplicate dates should be marged to show a count of posts per day
    # i.e ['2021-12-07', '2021-12-07', '2021-12-07', '2021-12-07', '2021-12-07']
    # becomes [{'2021-12-07',4}] etc
    datecount = {}
    for date in dates:
        if date in datecount:
            datecount[date] += 1
        else:
            datecount[date] = 1
    # remove '2021-09-09' - generic date of import along w/ anything before 2021-08
    datecount = {k: v for k, v in datecount.items() if k >= '2024-01-01' and k <='2024-12-31'}
    datecount = list(datecount.items())
    datecount.sort(key=lambda x: x[0])
    dates = [datetime.strptime(x[0], '%Y-%m-%d').date() for x in datecount]
    counts = [x[1] for x in datecount]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.plot(dates, counts, color="#42b983")
    plt.title('Victims per day in 2024\n© Ransomware.live')
    plt.xlabel('date')
    plt.xticks(rotation=90)
    plt.ylabel('# of posts')
    plt.savefig('docs/graphs/postsbyday2024.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def pie_posts_by_group():
    '''
    plot the number of posts by group in a pie
    '''
    posts = openjson(VICTIMS_FILE)
    group_counts = gcount(posts)
    group_counts = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
    group_counts = [x for x in group_counts if x[0] != 'clop']
    groups = [x[0] for x in group_counts]
    counts = [x[1] for x in group_counts]
    # ignoring the top 10 groups, merge the rest into "other"
    topgroups = groups[:10]
    topcounts = counts[:10]
    othercounts = counts[10:]
    othercount = sum(othercounts)
    topgroups.append('other')
    topcounts.append(othercount)
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    colours = ['#ffc09f','#ffee93','#fcf5c7','#a0ced9','#adf7b6','#e8dff5','#fce1e4','#fcf4dd','#ddedea','#daeaf6','#79addc','#ffc09f','#ffee93','#fcf5c7','#adf7b6']
    plt.pie(topcounts, labels=topgroups, autopct='%1.1f%%', startangle=140, labeldistance=1.1, pctdistance=0.8, colors=colours)
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=3)
    plt.text(0.5, 0.5, 'total : ' + str(sum(counts)), horizontalalignment='center', verticalalignment='center', transform=plt.gcf().transFigure)
    plt.title('Victims by group')
    plt.savefig('docs/graphs/grouppie.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def pie_posts_by_group_by_year(year):
    '''
    plot the number of posts by group in a pie
    '''
    posts = openjson(VICTIMS_FILE)
    group_counts = gcountYear(posts,year)
    group_counts = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
    group_counts = [x for x in group_counts]
    groups = [x[0] for x in group_counts]
    counts = [x[1] for x in group_counts]
    # ignoring the top 10 groups, merge the rest into "other"
    topgroups = groups[:10]
    topcounts = counts[:10]
    othercounts = counts[10:]
    othercount = sum(othercounts)
    topgroups.append('other')
    topcounts.append(othercount)
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    colours = ['#ffc09f','#ffee93','#fcf5c7','#a0ced9','#adf7b6','#e8dff5','#fce1e4','#fcf4dd','#ddedea','#daeaf6','#79addc','#ffc09f','#ffee93','#fcf5c7','#adf7b6']
    plt.pie(topcounts, labels=topgroups, autopct='%1.1f%%', startangle=140, labeldistance=1.1, pctdistance=0.8, colors=colours)
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=3)
    plt.text(0.5, 0.5, 'total : ' + str(sum(counts)), horizontalalignment='center', verticalalignment='center', transform=plt.gcf().transFigure)
    plt.title('Victims by group in '+ str(year))
    plt.savefig('docs/graphs/grouppie' + str(year) + '.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def pie_posts_by_group_by_month(year,month=0):
    '''
    plot the number of posts by group in a pie
    '''
    posts = openjson(VICTIMS_FILE)
    #group_counts = gcountYear(posts,year)
    group_counts = gcountMonth(posts,year,month)
    group_counts = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
    group_counts = [x for x in group_counts]
    groups = [x[0] for x in group_counts]
    counts = [x[1] for x in group_counts]
    # ignoring the top 10 groups, merge the rest into "other"
    topgroups = groups[:10]
    topcounts = counts[:10]
    othercounts = counts[10:]
    othercount = sum(othercounts)
    topgroups.append('other')
    topcounts.append(othercount)
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    colours = ['#ffc09f','#ffee93','#fcf5c7','#a0ced9','#adf7b6','#e8dff5','#fce1e4','#fcf4dd','#ddedea','#daeaf6','#79addc','#ffc09f','#ffee93','#fcf5c7','#adf7b6']
    plt.pie(topcounts, labels=topgroups, autopct='%1.1f%%', startangle=140, labeldistance=1.1, pctdistance=0.8, colors=colours)
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=3)
    plt.text(0.5, 0.5, 'total : ' + str(sum(counts)), horizontalalignment='center', verticalalignment='center', transform=plt.gcf().transFigure)
    if month == 0:
        plt.title('Victims by group in '+ str(year))
        plt.savefig('docs/graphs/grouppie' + str(year) + '.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    elif month < 10: 
        plt.title('Victims by group in 0'+ str(month) + '/' + str(year))
        plt.savefig('docs/graphs/grouppie' + str(year) + '0' + str(month) + '.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    else: 
        plt.title('Victims by group in '+ str(month) + '/' + str(year))
        plt.savefig('docs/graphs/grouppie' + str(year) + str(month) + '.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def trend_posts_per_day_month(year,month=0):
    '''
    plot the trend of the number of posts per day
    '''
    posts = openjson(VICTIMS_FILE)
    dates = []
    for post in posts:
        dates.append(post['published'][0:10])
    # list of duplicate dates should be marged to show a count of posts per day
    # i.e ['2021-12-07', '2021-12-07', '2021-12-07', '2021-12-07', '2021-12-07']
    # becomes [{'2021-12-07',4}] etc
    datecount = {}
    for date in dates:
        if date in datecount:
            datecount[date] += 1
        else:
            datecount[date] = 1
    # remove '2021-09-09' - generic date of import along w/ anything before 2021-08
    if month == 0:
        date_debut=str(year)+'01-01' 
        date_fin=str(year)+'12-31'
    elif month < 10:
        date_debut=str(year)+'-0'+str(month)+'-01' 
        date_fin=str(year)+'-0'+str(month)+'-'+str(last_day_of_month(month,year))
    else:
        date_debut=str(year)+'-'+str(month)+'-01' 
        date_fin=str(year)+'-'+str(month)+'-'+str(last_day_of_month(month,year))
    #datecount = {k: v for k, v in datecount.items() if k >= '2023-01-01' and k <='2023-12-31'}
    datecount = {k: v for k, v in datecount.items() if k >= date_debut and k <= date_fin}
    datecount = list(datecount.items())
    datecount.sort(key=lambda x: x[0])
    dates = [datetime.strptime(x[0], '%Y-%m-%d').date() for x in datecount]
    counts = [x[1] for x in datecount]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.plot(dates, counts, color="#42b983")
    plt.xlabel('Date\n© Ransomware.live')
    plt.xticks(rotation=90)
    plt.ylabel('# of Victims')
    if month == 0:
        plt.title('Victims per day in '+str(year))
        plt.savefig('docs/graphs/postsbyday'+str(year)+'.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    if month < 10:
        plt.title('Victims per day in 0'+ str(month)+'/' + str(year))
        plt.savefig('docs/graphs/postsbyday'+str(year)+'0'+str(month)+'.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    if month > 9:
        plt.title('Victims per day in '+ str(month)+'/' + str(year))
        plt.savefig('docs/graphs/postsbyday'+str(year)+str(month)+'.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def plot_posts_by_group_by_month(year,month=0):
    '''
    plot the number of posts by group in a barchart
    '''
    posts = openjson(VICTIMS_FILE)
    # group_counts = gcountYear(posts,year)
    group_counts = gcountMonth(posts,year,month)
    group_counts = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
    group_counts = [x for x in group_counts]
    groups = [x[0] for x in group_counts]
    counts = [x[1] for x in group_counts]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.figure(figsize=(15, 8))  # Increase the width and height as needed
    plt.bar(groups, counts, color="#42b983")
    plt.xlabel('Group Name\n© Ransomware.live')
    plt.xticks(rotation=90)
    plt.ylabel('# of Victims')
    if month == 0:
        plt.title('Victims per group in '+str(year))
        plt.savefig('docs/graphs/postsbygroup'+str(year)+'.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    if month < 10:
        plt.title('Victims per group in 0'+ str(month)+'/' + str(year))
        plt.savefig('docs/graphs/postsbygroup'+str(year)+'0'+str(month)+'.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    if month > 9:
        plt.title('Victims per group in '+ str(month)+'/' + str(year))
        plt.savefig('docs/graphs/postsbygroup'+str(year)+str(month)+'.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def plot_victims_by_month():
    # Read the JSON file and load the data
    data = openjson(VICTIMS_FILE)
    
    # Count the number of post titles (victims) by month for the years 2022 and 2023
    year_data = {}
    for post in data:
        # Assuming the JSON data has a "published" field and a "post_title" field
        date = post['published']
        title = post['post_title']
        
        year = date[:4]  # Extract the year from the date
        
        if year in ['2022', '2023','2024']:
            if year not in year_data:
                year_data[year] = {}
            
            month = date[5:7]  # Extract the month from the date
            
            if month not in year_data[year]:
                year_data[year][month] = 0
            
            year_data[year][month] += 1

    # Prepare the data for plotting
    months = ['{:02d}'.format(i) for i in range(1, 13)]
    years = ['2022', '2023', '2024']
    data_2022 = [year_data['2022'].get(month, 0) for month in months]
    data_2023 = [year_data['2023'].get(month, 0) for month in months]
    data_2024 = [year_data['2024'].get(month, 0) for month in months]

    # Set the figure size
    plt.figure(figsize=(12, 6))
    plt.set_loglevel('WARNING')
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"

    # Plotting the line chart
    plt.plot(months, data_2022, label='2022')
    plt.plot(months, data_2023, label='2023')
    plt.plot(months, data_2024, label='2024')

    # Customize the chart
    #plt.title('Number of Victims by Month (2022-2023)')
    plt.title('Number of Victims by Month (2022-2024)')
    plt.xlabel('Month')
    text_color = '#42b983'
    plt.text(0.5, -0.2, '© Ransomware.live', size=10, ha='center', transform=plt.gca().transAxes, color=text_color)
    plt.ylabel('Number of Victims')
    plt.legend()

    # Add grid
    plt.grid(True)
    plt.tight_layout()

    # Save the chart as PNG
    plt.savefig('docs/graphs/victims_by_month.png')
    plt.clf()
    plt.cla()
    add_watermark('docs/graphs/victims_by_month.png')



def plot_victims_by_month_cumulative():
    # Read the JSON file and load the data
    data = openjson(VICTIMS_FILE)

    # Get current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Count the number of post titles (victims) by month for the years 2022 and 2023
    year_data = {}
    for post in data:
        # Assuming the JSON data has a "published" field and a "post_title" field
        date = post['published']
        title = post['post_title']

        year = date[:4]  # Extract the year from the date

        if year in ['2022', '2023','2024']:
            if year not in year_data:
                year_data[year] = {}

            month = date[5:7]  # Extract the month from the date

            if month not in year_data[year]:
                year_data[year][month] = 0

            year_data[year][month] += 1

    # Prepare the data for plotting
    months = ['{:02d}'.format(i) for i in range(1, 13)]
    years = ['2022', '2023', '2024']

    # Calculate cumulative victims for each year
    cumulative_data = {}
    for year in years:
        cumulative_data[year] = []
        cumulative_sum = 0
        for month in months:
            cumulative_sum += year_data[year].get(month, 0)
            cumulative_data[year].append(cumulative_sum)

    # Set the figure size
    plt.figure(figsize=(12, 6))
    plt.set_loglevel('WARNING')
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"

    # Plotting the line chart
    plt.plot(months, cumulative_data['2022'], label='2022')
    plt.plot(months, cumulative_data['2023'], label='2023')
    plt.plot(months, cumulative_data['2024'], label='2024')

    # Customize the chart
    plt.title('Cumulative Number of Victims by Month (2022-2024)')
    plt.xlabel('Month')
    text_color = '#42b983'
    plt.text(0.5, -0.2, '© Ransomware.live', size=10, ha='center', transform=plt.gca().transAxes, color=text_color)
    plt.ylabel('Cumulative Number of Victims')
    plt.legend()

    # Add grid
    plt.grid(True)
    plt.tight_layout()

    # Save the chart as PNG
    plt.savefig('docs/graphs/victims_by_month_cumulative.png')
    plt.clf()
    plt.cla()
    add_watermark('docs/graphs/victims_by_month_cumulative.png')


def create_victims_per_day_graph(target_year,target_month):
    # Load data from posts.json
    posts_data = openjson(VICTIMS_FILE)

    # Filter posts within the specified month and year
    filtered_posts = [post for post in posts_data if datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f').month == target_month and datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f').year == target_year]

    # Count the number of posts for each day
    daily_post_count = {}
    for post in filtered_posts:
        post_date = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f').day
        daily_post_count[post_date] = daily_post_count.get(post_date, 0) + 1

    # Prepare data for plotting
    days = list(daily_post_count.keys())
    post_counts = list(daily_post_count.values())

    # Convert target_month to the name of the month
    target_month_name = calendar.month_name[target_month]

    text_color = '#42b983'

    # Create a bar graph with the specified color
    plt.bar(days, post_counts, color='#42b983')
    plt.xlabel(target_month_name + ' ' + str(target_year), color=text_color)
    plt.text(0.5, -0.2, '© Ransomware.live', size=10, ha='center', transform=plt.gca().transAxes, color=text_color)
    plt.ylabel('Number of victims',color=text_color)
    plt.title(f'Victims per day - {target_month_name} {target_year}',color=text_color)

    plt.xticks(days, color=text_color)
    plt.yticks(color=text_color)

    # Set the color of axis labels and legend
    ax = plt.gca()
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.tick_params(axis='x', colors=text_color)
    ax.tick_params(axis='y', colors=text_color)

    # Set the color of the spines (borders) around the graph
    ax.spines['bottom'].set_color(text_color)
    ax.spines['top'].set_color(text_color)
    ax.spines['left'].set_color(text_color)
    ax.spines['right'].set_color(text_color)

    plt.tight_layout()

    # Save the plot as a PNG image
    month2 = f'{target_month:02}'
    plt.savefig(f'docs/graphs/victims_per_day_{target_year}{month2}.png')
    plt.close()  # Close the figure to prevent showing the plot

def wordcloud():
    try:
    # Read the JSON data from posts.json
        data = openjson(VICTIMS_FILE)
    except:
        errlog(f'WordCloud: Error reading {VICTIMS_FILE}')

    # Filter the posts for the year 2024
    data = [post for post in data if 'discovered' in post and post['discovered'].startswith('2024')]

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
        stdlog("WordCloud generated")
        add_watermark(output_path)
    except:
        errlog("WordCloud : Error while saving image")

def statsgroup(specific_group_name):
    # Reset variables
    victim_counts = {}
    dates = []
    counts = []

    # Read posts.json and filter posts for the specific group name and start date
    with open('./data/victims.json', 'r') as posts_file:
        posts_data = json.load(posts_file)
        filtered_posts = [
            post for post in posts_data
            if post['group_name'] == specific_group_name
            and datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f') >= datetime(2022, 1, 1)
        ]

    # Count the number of victims per day
    for post in filtered_posts:
        date = datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f').date()
        victim_counts[date] = victim_counts.get(date, 0) + 1 

    # Sort the victim counts by date
    sorted_counts = sorted(victim_counts.items())

    # Extract the dates and counts for plotting
    dates, counts = zip(*sorted_counts)

    start_date = datetime(2022, 1, 1).date()

    # Plot the graph
    plt.clf()
    # Create a new figure and axes for each group with a larger figure size
    fig,ax = plt.subplots(figsize=(10, 3))  # Adjust the width (10) and height (6) as desired

    # plt.plot(dates, counts)
    ax.bar(dates, counts, color = '#42b983')
    ax.set_xlabel('Date\nRansomware.live', color = '#42b983')
    ax.set_ylabel('Number of Victims', color = '#42b983')
    ax.set_title('Number of Victims for Group: ' + specific_group_name, color = '#42b983')
    ax.tick_params(axis='x', rotation=45)
    # Set the x-axis limits
    ax.set_xlim(start_date, datetime.now().date())
    # Format y-axis ticks as whole numbers without a comma separator
    
    plt.tight_layout()

    # Save the graph as an image file
    plt.savefig('docs/graphs/stats-' + specific_group_name + '.png')
    plt.close(fig)


def generate_ransomware_map():
    json_path = './data/victims.json'
    html_path = 'docs/map.html'
    md_path = 'docs/map.md'
    current_year = datetime.now().year

    # Load JSON data from file
    stdlog('Reading posts.json ...')
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Convert data into a DataFrame
    df = pd.DataFrame(data)

    # Convert 'date' column to datetime, assuming the format is 'YYYY-MM-DD HH:MM:SS.ssssss'
    df['discovered'] = pd.to_datetime(df['discovered'], errors='coerce')

    stdlog('Filtering victims')
    # Filter for rows where the year is current_year
    df_currentyear = df[df['discovered'].dt.year == current_year]

    # Filter rows where 'country' is not None or empty
    filtered_df = df_currentyear[df_currentyear['country'].notna() & (df_currentyear['country'] != '')].copy()

    # Aggregate data by country code, counting entries per country code
    country_counts = filtered_df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']

    stdlog('Getting geocoding ...')
    # Apply geocoding
    country_counts['coords'] = country_counts['country'].apply(get_coordinates)

    title_html = '''
                 <h3 align="center" style="font-size:16px"><b>© {} <a href="https://www.ransomware.live/">Ransomware.live</a></b></h3>
                 '''.format(current_year) 

    stdlog('Initialize Map')
    # Create a map
    map = folium.Map(location=[20, 0], zoom_start=2)

    map.get_root().html.add_child(folium.Element(title_html))

    # Scaling factor for the radius
    scale_factor = 1

    stdlog('Adding point on map ...')
    # Add points to the map
    for idx, row in country_counts.iterrows():
        if row['coords'] is not None:  # Ensure the coordinates are not None
            lat, lon = row['coords']
            if lat is not None and lon is not None:  # Ensure both latitude and longitude are available
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=scale_factor * row['count']**0.5,  # Scale radius based on square root of count
                    popup=f"<a href='https://www.ransomware.live/#/country/{row['country'].lower()}' target='_parent'>{get_country_name(row['country'])}</a>: {row['count']} victim(s)",
                    color='red',
                    fill=True,
                    fill_opacity=0.7
                ).add_to(map)
            else:
                errlog("2) Skipping " + row['country'] + " due to missing coordinates.")
        else:
            stdlog("2) Skipping " + row['country'] + " due to missing coordinates.")

    # Save or show the map
    stdlog('Writing Map ...')
    map.save(html_path)
    stdlog('Writing markdown file ...')
    current_datetime = datetime.now().isoformat()
    content = f"""
### 🗺️ Worldmap for ransomware's attacks in {current_year}

[filename](map.html ':include')

_Last update: {current_datetime}_
"""
    with open(md_path, 'w') as file:
        file.write(content)


import matplotlib.pyplot as plt
import pandas as pd

def generate_execution_time_graphs():
    # Define the path to the log file and the output image files
    log_file_path = '/var/log/ransomwarelive.log'
    output_image_days = './docs/admin/execution_times-days.png'
    output_image_daily = './docs/admin/execution_times-daily.png'
    output_image_monthly = './docs/admin/execution_times-monthly.png'

    # Warning value in minutes
    warning = 120

    # Read the log file into a pandas DataFrame
    try:
        # Read the log file with appropriate column names
        log_df = pd.read_csv(log_file_path, header=None, names=['datetime', 'scraping_time', 'parsing_time', 'markdown_time', 'total_execution_time'])
        log_df['datetime'] = pd.to_datetime(log_df['datetime'])
        
        # Convert times from seconds to minutes
        log_df['scraping_time'] = log_df['scraping_time'] / 60
        log_df['parsing_time'] = log_df['parsing_time'] / 60
        log_df['markdown_time'] = log_df['markdown_time'] / 60
        log_df['total_execution_time'] = log_df['total_execution_time'] / 60
        
        # Calculate the other time component
        log_df['other_time'] = log_df['total_execution_time'] - (log_df['parsing_time'] + log_df['scraping_time'] + log_df['markdown_time'])
        
        # Set the datetime as the index for easier plotting
        log_df.set_index('datetime', inplace=True)
        
        # Filter data for the last 3 days
        last_3_days_df = log_df[log_df.index >= (pd.Timestamp.now() - pd.Timedelta(days=3))]
        
        # Plot the execution times for the last 3 days as a cumulative bar graph
        ax = last_3_days_df[['scraping_time', 'parsing_time', 'markdown_time', 'other_time']].plot(kind='bar', stacked=True, figsize=(12, 8), color=['#1f77b4', '#ff7f0e', '#9467bd', '#2ca02c'])
        plt.axhline(y=warning, color='r', linestyle='--', label='Warning Level')
        plt.title('Execution Times for the Last 3 Days')
        plt.xlabel('Date and Time')
        plt.ylabel('Execution Time (minutes)')
        plt.xticks(rotation=45)
        plt.legend(title='Execution Time Components')
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.savefig(output_image_days)
        plt.close()
        
        # Resample data to get daily averages
        daily_avg_df = log_df.resample('D').mean()
        
        # Plot the daily average execution times
        ax = daily_avg_df[['scraping_time', 'parsing_time', 'markdown_time', 'other_time']].plot(kind='bar', stacked=True, figsize=(12, 8), color=['#1f77b4', '#ff7f0e', '#9467bd', '#2ca02c'])
        plt.axhline(y=warning, color='r', linestyle='--', label='Warning Level')
        plt.title('Average Daily Execution Times')
        plt.xlabel('Date')
        plt.ylabel('Average Execution Time (minutes)')
        plt.xticks(ticks=range(len(daily_avg_df.index)), labels=[date.strftime('%Y-%m-%d') for date in daily_avg_df.index], rotation=45)
        plt.legend(title='Execution Time Components')
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.savefig(output_image_daily)
        plt.close()
        
        # Resample data to get monthly averages
        monthly_avg_df = log_df.resample('M').mean()
        
        # Plot the monthly average execution times
        ax = monthly_avg_df[['scraping_time', 'parsing_time', 'markdown_time', 'other_time']].plot(kind='bar', stacked=True, figsize=(12, 8), color=['#1f77b4', '#ff7f0e', '#9467bd', '#2ca02c'])
        plt.axhline(y=warning, color='r', linestyle='--', label='Warning Level')
        plt.title('Average Monthly Execution Times')
        plt.xlabel('Month')
        plt.ylabel('Average Execution Time (minutes)')
        plt.xticks(ticks=range(len(monthly_avg_df.index)), labels=[date.strftime('%Y-%m') for date in monthly_avg_df.index], rotation=45)
        plt.legend(title='Execution Time Components')
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.savefig(output_image_monthly)
        plt.close()
        
        stdlog(f'Execution time graphs saved to {output_image_days}, {output_image_daily}, and {output_image_monthly}')
    except FileNotFoundError:
        errlog(f'Log file not found at {log_file_path}')
    except pd.errors.ParserError:
        errlog(f'Error parsing the log file at {log_file_path}')
    except Exception as e:
        errlog(f'An unexpected error occurred: {e}')



def plot_group_activity(year):
    # Load the data
    input_file='./data/victims.json'
    output_file=f'./docs/graphs/group-activity-{str(year)}.png'
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Convert the JSON data into a DataFrame
    df = pd.json_normalize(data)

    # Convert the 'discovered' column to datetime
    df['discovered'] = pd.to_datetime(df['discovered'])

    # Extract year and month from the 'discovered' date
    df['year'] = df['discovered'].dt.year
    df['month'] = df['discovered'].dt.strftime('%b')

    # Filter the data for the specified year only
    df_year = df[df['year'] == year]

    # For each group, find the first and last entry of the specified year
    group_min_max_dates = df_year.groupby('group_name')['discovered'].agg(['min', 'max']).reset_index()

    # Check for previous entries in years before the specified year
    df_previous_years = df[df['year'] < year]
    previous_entries = df_previous_years.groupby('group_name')['discovered'].min().reset_index()

    # Check for entries in the years after the specified year
    df_next_years = df[df['year'] > year]
    next_entries = df_next_years.groupby('group_name')['discovered'].min().reset_index()

    # Merge this information with the data for the specified year
    merged_df = pd.merge(group_min_max_dates, previous_entries, on='group_name', how='left', suffixes=('', '_previous'))
    merged_df = pd.merge(merged_df, next_entries, on='group_name', how='left', suffixes=('', '_next'))

    # If there was a previous entry, set the start date to January of the specified year
    month_mapping = {month: i+1 for i, month in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}
    merged_df['start_month_num'] = merged_df.apply(
        lambda x: 1 if pd.notna(x['discovered']) else month_mapping[x['min'].strftime('%b')], axis=1
    )

    # If there is a next entry in future years, set the end date to December of the specified year
    merged_df['end_month_num'] = merged_df.apply(
        lambda x: 12 if pd.notna(x['discovered_next']) else month_mapping[x['max'].strftime('%b')], axis=1
    )

    # Plotting the lines with the adjusted start and end dates
    plt.figure(figsize=(18, 24))  # Increased height for more space between group names
    for _, row in merged_df.iterrows():
        plt.plot([row['start_month_num'], row['end_month_num']], [row['group_name'], row['group_name']], marker='o')

    # Formatting the plot
    plt.yticks(range(len(merged_df)), merged_df['group_name'])
    plt.xticks(range(1, 13), month_mapping.keys())
    plt.xlabel('Month')
    plt.ylabel('Ransomware group')
    plt.title(f'Group activity for {year}',fontsize=20)
    plt.grid(True)

    # Save the figure
    plt.savefig(output_file)
    add_watermark(output_file)



