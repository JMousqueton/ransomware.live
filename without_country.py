import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Read the posts from posts.json
with open('posts.json', 'r') as file:
    posts = json.load(file)

# Filter posts discovered in 2024
posts_2024 = [post['post_title'] for post in posts if (post['discovered'].startswith('2024') and not post['country'])]

if posts_2024: 
    # Email configurations
    sender_email = 'notify@ransomware.live'  # Replace with your email
    receiver_email = 'julien@mousqueton.io'  # Replace with recipient's email
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
        server = smtplib.SMTP('localhost', 25)
        server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        print("Email could not be sent:", str(e))
    finally:
        server.quit()
else:
    print("No new posts wihtou country")

