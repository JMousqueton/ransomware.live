import pandas as pd
import json
import folium
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from mypycountries import get_coordinates, get_country_name # https://github.com/JMousqueton/MyPyCountries 
from ransomwarelive import stdlog, dbglog, errlog

file_path = './docs/map.md'

current_year = datetime.now().year

# Load JSON data from file
stdlog('Reading posts.json ...')
with open('./data/victims.json', 'r') as file:
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
            #print('--->',row['coords'])
        else:
            stdlog("2) Skipping " + row['country'] + " due to missing coordinates.")
    else:
        stdlog("2) Skipping " + row['country'] + " due to missing coordinates.")

# Save or show the map
stdlog('Writing Map ...')
map.save('docs/map.html')
stdlog('Writing markdown file ...')
current_datetime = datetime.now().isoformat()
content = f"""
### 🗺️ Worldmap for ransomware's attacks in {current_year}

[filename](map.html ':include')

_Last update: {current_datetime}_
"""
with open(file_path, 'w') as file:
    file.write(content)
stdlog('done')
