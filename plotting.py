#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime, json, calendar
import matplotlib.pyplot as plt
#from datetime import datetime

from sharedutils import gcount, gcountYear, gcountMonth, last_day_of_month
from sharedutils import openjson

def plot_posts_by_group():
    '''
    plot the number of posts by group in a barchart
    '''
    posts = openjson('posts.json')
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
    posts = openjson('posts.json')
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
    plt.title('Vicitms by group in ' + str(year))
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
    posts = openjson('posts.json') 
    seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
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
    posts = openjson('posts.json')
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
    dates = [datetime.datetime.strptime(x[0], '%Y-%m-%d').date() for x in datecount]
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
    posts = openjson('posts.json')
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
    dates = [datetime.datetime.strptime(x[0], '%Y-%m-%d').date() for x in datecount]
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
    posts = openjson('posts.json')
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
    dates = [datetime.datetime.strptime(x[0], '%Y-%m-%d').date() for x in datecount]
    counts = [x[1] for x in datecount]
    plt.rcParams['text.color'] = "#42b983"
    plt.rcParams['axes.labelcolor'] = "#42b983"
    plt.rcParams['xtick.color'] = "#42b983"
    plt.rcParams['ytick.color'] = "#42b983"
    plt.plot(dates, counts, color="#42b983")
    plt.title('posts per day in 2023\n© Ransomware.live')
    plt.xlabel('date')
    plt.xticks(rotation=90)
    plt.ylabel('# of posts')
    plt.savefig('docs/graphs/postsbyday2023.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def pie_posts_by_group():
    '''
    plot the number of posts by group in a pie
    '''
    posts = openjson('posts.json')
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
    plt.title('Vicitms by group')
    plt.savefig('docs/graphs/grouppie.png',dpi=300, bbox_inches="tight", pad_inches=0.1, frameon=False, transparent=True)
    plt.clf()
    plt.cla()

def pie_posts_by_group_by_year(year):
    '''
    plot the number of posts by group in a pie
    '''
    posts = openjson('posts.json')
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
    posts = openjson('posts.json')
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
    posts = openjson('posts.json')
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
    dates = [datetime.datetime.strptime(x[0], '%Y-%m-%d').date() for x in datecount]
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
    posts = openjson('posts.json')
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
    data = openjson('posts.json')
    
    # Count the number of post titles (victims) by month for the years 2022 and 2023
    year_data = {}
    for post in data:
        # Assuming the JSON data has a "published" field and a "post_title" field
        date = post['published']
        title = post['post_title']
        
        year = date[:4]  # Extract the year from the date
        
        if year in ['2022', '2023']:
            if year not in year_data:
                year_data[year] = {}
            
            month = date[5:7]  # Extract the month from the date
            
            if month not in year_data[year]:
                year_data[year][month] = 0
            
            year_data[year][month] += 1

    # Prepare the data for plotting
    months = ['{:02d}'.format(i) for i in range(1, 13)]
    years = ['2022', '2023']
    data_2022 = [year_data['2022'].get(month, 0) for month in months]
    data_2023 = [year_data['2023'].get(month, 0) for month in months]

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

    # Customize the chart
    plt.title('Number of Victims by Month (2022-2023)')
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



def plot_victims_by_month_cumulative():
    # Read the JSON file and load the data
    data = openjson('posts.json')

    # Count the number of post titles (victims) by month for the years 2022 and 2023
    year_data = {}
    for post in data:
        # Assuming the JSON data has a "published" field and a "post_title" field
        date = post['published']
        title = post['post_title']

        year = date[:4]  # Extract the year from the date

        if year in ['2022', '2023']:
            if year not in year_data:
                year_data[year] = {}

            month = date[5:7]  # Extract the month from the date

            if month not in year_data[year]:
                year_data[year][month] = 0

            year_data[year][month] += 1

    # Prepare the data for plotting
    months = ['{:02d}'.format(i) for i in range(1, 13)]
    years = ['2022', '2023']

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

    # Customize the chart
    plt.title('Cumulative Number of Victims by Month (2022-2023)')
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


def create_victims_per_day_graph(target_year,target_month):
    # Load data from posts.json
    posts_data = openjson('posts.json')

    # Filter posts within the specified month and year
    filtered_posts = [post for post in posts_data if datetime.datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f').month == target_month and datetime.datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f').year == target_year]

    # Count the number of posts for each day
    daily_post_count = {}
    for post in filtered_posts:
        post_date = datetime.datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f').day
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

