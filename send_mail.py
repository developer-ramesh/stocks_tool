import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email details
smtp_server = 'mail.capsquery.com'
smtp_port = 465
username = 'arijit@capsquery.com'
password = 'KP@010823'
sender_email = 'ramesh@capsquery.com'
receiver_email = 'info.ramesh.co@gmail.com'
subject = 'Market Cap Update'

# Example market cap values
existing_market_cap = 300000.50
stock = {'Market Cap': 256503.00}

# Formatting the message
message_parts = []
message_parts.append(f"Market Cap value decreased, Prev: {existing_market_cap:.0f} Last: {stock['Market Cap']:.0f}")
formatted_message = " ".join(message_parts)

# Create MIME multipart message
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject

# Attach the message body
msg.attach(MIMEText(formatted_message, 'plain'))

try:
    # Connect to the SMTP server and send email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
