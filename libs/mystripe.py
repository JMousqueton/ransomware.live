import os
import stripe
from dotenv import load_dotenv
from datetime import datetime, timedelta
import calendar
import matplotlib.pyplot as plt
from ransomwarelive import stdlog, errlog

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path=env_path)
stripe.api_key = os.getenv('STRIPE_API_KEY')

current_year = datetime.now().year
# Define the output file as a global variable
output_file = './docs/admin/budget_stripe-' + str(current_year) + '.png'

# Function to get all payments for a specific month
def get_monthly_payments(year, month):
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    payments = stripe.PaymentIntent.list(
        created={
            'gte': start_timestamp,
            'lte': end_timestamp,
        },
        limit=100  # Adjust as necessary, Stripe max limit is 100
    )

    return payments

# Function to get all payouts for a specific month
def get_monthly_payouts(year, month):
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    payouts = stripe.Payout.list(
        created={
            'gte': start_timestamp,
            'lte': end_timestamp,
        },
        limit=100  # Adjust as necessary, Stripe max limit is 100
    )

    return payouts

# Function to get monthly payments and payouts
def get_monthly_financials(year):
    months = range(1, 13)
    monthly_payments = []
    monthly_payouts = []
    payment_counts = []

    for month in months:
        payments = get_monthly_payments(year, month)
        total_payments = sum(payment.amount for payment in payments['data']) / 100  # Convert cents to euros
        monthly_payments.append(total_payments)
        payment_counts.append(len(payments['data']))

        payouts = get_monthly_payouts(year, month)
        total_payouts = sum(payout.amount for payout in payouts['data']) / 100  # Convert cents to euros
        monthly_payouts.append(total_payouts)

    return monthly_payments, monthly_payouts, payment_counts

# Function to plot the combined graph and save it to a file
def plot_financials(year):
    monthly_payments, monthly_payouts, payment_counts = get_monthly_financials(year)
    cumulative_payouts = [sum(monthly_payouts[:i+1]) for i in range(len(monthly_payouts))]
    months = [calendar.month_name[i] for i in range(1, 13)]
    
    # Calculate the cumulative payout for December
    cumulative_payout_december = cumulative_payouts[-1]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Bar chart for monthly payments received
    bars = ax.bar(months, monthly_payments, color='skyblue', label='Monthly Payments')

    # Line chart for cumulative payouts
    ax.plot(months, cumulative_payouts, marker='o', color='red', label='Cumulative Payouts')

    # Annotate bars with the number of payments
    for bar, count in zip(bars, payment_counts):
        if count > 0:  # Only annotate if the count is greater than 0
            height = bar.get_height()
            ax.annotate(f'{count}', 
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10)

    # Display the cumulative payout for December
    ax.text(11, cumulative_payout_december, f'€{cumulative_payout_december:.2f}', 
            color='red', ha='center', va='bottom', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

    ax.set_xlabel('Month')
    ax.set_ylabel('Amount in Euros')
    ax.set_title(f'Financial Overview in {year}')
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    plt.savefig(output_file)

# Check if the script should run based on the file modification date
def should_run():
    if os.path.exists(output_file):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(output_file))
        if datetime.now() - file_mod_time < timedelta(hours=24):
            return False
    return True

# Function to get total paid by email and plot the graph
def plot_payments_by_email():
    # Retrieve all charges
    charges = stripe.Charge.list(limit=100)
    payments_by_email = {}

    # Extract customer info from charges
    for charge in charges.auto_paging_iter():
        if charge.paid:
            customer_id = charge.customer
            customer = stripe.Customer.retrieve(customer_id)
            email = customer.email
            amount_paid = charge.amount / 100  # Convert amount to euros
            if email in payments_by_email:
                payments_by_email[email]['amount'] += amount_paid
                payments_by_email[email]['count'] += 1
            else:
                payments_by_email[email] = {'amount': amount_paid, 'count': 1}

    # Sort emails by total amount paid
    sorted_payments_by_email = dict(sorted(payments_by_email.items(), key=lambda item: item[1]['amount'], reverse=True))

    # Plot the data
    emails = list(sorted_payments_by_email.keys())[:100]  # Get top 10 emails
    amounts = [sorted_payments_by_email[email]['amount'] for email in emails]
    counts = [sorted_payments_by_email[email]['count'] for email in emails]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(emails, amounts, color='skyblue')
    ax.set_xlabel('Amount in Euros')
    ax.set_ylabel('Sponsors')
    ax.set_title('Sponsors by Total Payments')

    # Annotate bars with the payment amounts and counts
    for bar, amount, count in zip(bars, amounts, counts):
        ax.annotate(f'€{amount:.2f} ({count})', 
                    xy=(amount, bar.get_y() + bar.get_height() / 2),
                    xytext=(3, 0),  # 3 points horizontal offset
                    textcoords="offset points",
                    ha='left', va='center', fontsize=10)

    fig.tight_layout()
    plt.savefig('./docs/admin/budget_sponsors.png')

def generatestripe():
    if should_run():
        plot_financials(current_year)
        plot_payments_by_email()
        stdlog('Stripe graph generated')
    else:
        errlog("The script has been executed within the last 24 hours. Exiting.")

