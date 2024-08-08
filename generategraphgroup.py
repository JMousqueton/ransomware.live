import json
import datetime
import matplotlib.pyplot as plt

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
            and datetime.datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f') >= datetime.datetime(2022, 1, 1)
        ]

    # Count the number of victims per day
    for post in filtered_posts:
        date = datetime.datetime.strptime(post['published'], '%Y-%m-%d %H:%M:%S.%f').date()
        victim_counts[date] = victim_counts.get(date, 0) + 1 

    # Sort the victim counts by date
    sorted_counts = sorted(victim_counts.items())

    # Extract the dates and counts for plotting
    dates, counts = zip(*sorted_counts)

    start_date = datetime.datetime(2022, 1, 1).date()

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
    ax.set_xlim(start_date, datetime.datetime.now().date())
    # Format y-axis ticks as whole numbers without a comma separator
    
    plt.tight_layout()

    # Save the graph as an image file
    plt.savefig('docs/graphs/stats-' + specific_group_name + '.png')
    plt.close(fig)

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


# Read groups.json and extract group names
with open('./data/groups.json', 'r') as groups_file:
    groups_data = json.load(groups_file)
    group_names = [group['name'] for group in groups_data]

for group_name in group_names:
    try:
        statsgroup(group_name)
    except:  
        print("no graph for " + group_name) 
        pass
