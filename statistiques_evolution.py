import json
from datetime import datetime, timedelta

# Read the JSON file
with open('posts.json') as f:
    data = json.load(f)

# Get the current date
current_date = datetime.now()
current_year = current_date.year
current_month_name = current_date.strftime('%B')

next_month = current_date + timedelta(days=30)
previous_year = current_date.year - 1 

# Get the two-digit representation of the next month
next_month_digits = next_month.strftime('%m')

# Define the start and end dates for filtering
start_date_2022 = str(previous_year)+'-01-01'
end_date_2022 = str(previous_year)+'-' + str(next_month_digits) + '-01'

# Define the start and end dates for 2023 (January to May)
start_date_2023 = str(current_year)+'-01-01'
#end_date_2023 = str(current_year)+'-' + str(next_month_digits) + '01'
end_date_2023 = '2023-12-31'
# Initialize counters
count_2022 = 0
count_2023 = 0

# Iterate over the posts and count the titles within the specified date ranges
for post in data:
    published_date = post['published']
    if start_date_2022 <= published_date <= end_date_2022:
        count_2022 += 1
    elif start_date_2023 <= published_date <= end_date_2023:
        count_2023 += 1

# Calculate the percentage increase
percentage_increase = ((count_2023 - count_2022) / count_2022) * 100

# Print the counts and the percentage increase
print("Number of victims from January to \033[1m"+ current_month_name + "\033[0m " + str(previous_year)+":", count_2022)
print("Number of victims from January to \033[1m"+ current_month_name + "\033[0m " + str(current_year)+":", count_2023)
print("Percentage between 2022 and 2023: \033[1m{:.2f}%\033[0m".format(percentage_increase))
