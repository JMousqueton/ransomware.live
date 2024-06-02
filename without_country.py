import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()  # This loads the varia

# Load environment variables
SMTP_SERVER = os.getenv('SMTP_SERVER', 'localhost')
SMTP_PORT = int(os.getenv('SMTP_PORT', 25))  # Default to port 25 if not specified
EMAIL_FROM = os.getenv('EMAIL_FROM', 'default_sender@example.com')
EMAIL_TO = os.getenv('EMAIL_TO', 'default_receiver@example.com')

# Read the posts from posts.json
with open('posts.json', 'r') as file:
    posts = json.load(file)

# Filter posts discovered in 2024
posts_2024 = [post['post_title'] for post in posts if (post['discovered'].startswith('2024') and not post['country'])]
# Remove entries containing "**" from posts_2024
posts_2024 = [post for post in posts_2024 if "**" not in post]

if posts_2024: 
    # Email configurations
    sender_email = EMAIL_FROM
    receiver_email = EMAIL_TO
    subject = '[Action required] New post(s) without country'

    # Compose email
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    body = "List of new post(s) which required action :\n\n"
    body += "\n".join(posts_2024)
    message.attach(MIMEText(body, 'plain'))

    # Connect to local SMTP server and send email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        print("Email could not be sent:", str(e))
    finally:
        server.quit()
else:
    print("No new posts wihtou country")

