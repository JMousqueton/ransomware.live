import json
from datetime import datetime
import pandas as pd
import plotly.express as px

# Load the JSON data from the file
with open('posts.json', 'r') as file:
    data = json.load(file)

# Initialize dictionaries to store the posting frequency for each group
group_dates = {}

# Extract the group name and timestamp from each post
for post in data:
    group_name = post['group_name']
    timestamp = post['discovered']
    date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f').replace(microsecond=0)

    # Filter dates that are after January 1, 2022
    if date.date() >= datetime(2022, 1, 1).date():
        # Update the posting dates for each group
        if group_name in group_dates:
            group_dates[group_name].append(date)
        else:
            group_dates[group_name] = [date]

# Calculate the frequency of each group
group_frequencies = {group_name: len(dates) for group_name, dates in group_dates.items()}

# Sort the groups based on frequencies in descending order
sorted_groups = sorted(group_frequencies, key=group_frequencies.get, reverse=True)

# Create a list to store the data for each group
group_data = []

# Accumulate the dates and frequencies for all groups
for group_name in sorted_groups:
    dates = group_dates[group_name]
    group_data.extend([(date, group_name) for date in dates])

# Create a dataframe from the combined data
df = pd.DataFrame(group_data, columns=['Date', 'Group'])

# Create a plot of posting frequency for all groups over time
fig = px.histogram(df, x='Date', color='Group', title='Posting Frequency for All Groups')
fig.update_layout(xaxis_title='Date', yaxis_title='Frequency')

# Save the plot as a PNG image
fig.write_image('docs/combined_posting_frequency.png')

