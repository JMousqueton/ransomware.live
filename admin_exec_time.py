import matplotlib.pyplot as plt
import pandas as pd

# Define the path to the log file and the output image files
log_file_path = '/var/log/ransomwarelive.log'
output_image_days = './docs/admin/execution_times-days.png'
output_image_daily = './docs/admin/execution_times-daily.png'
output_image_monthly = './docs/admin/execution_times-monthly.png'

# Warning value in minutes
warning = 100

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
    
    print(f'Execution time graphs saved to {output_image_days}, {output_image_daily}, and {output_image_monthly}')
except FileNotFoundError:
    print(f'Log file not found at {log_file_path}')
except pd.errors.ParserError:
    print(f'Error parsing the log file at {log_file_path}')
except Exception as e:
    print(f'An unexpected error occurred: {e}')
