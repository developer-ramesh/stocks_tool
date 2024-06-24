import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_server = 'mail.capsquery.com'
smtp_port = 587
username = 'arijit@capsquery.com'
password = 'KP@010823'
sender_email = 'ramesh@capsquery.com'
receiver_email = 'info.ramesh.co@gmail.com'
subject = 'Market Cap Update'

# Email body
formatted_message = """\
Hello,

This is an automated email to notify you that the market cap data has been updated.

Thank you,
Stock Market Bot
"""

# Create MIME multipart message
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(formatted_message, 'plain'))

def send_email():
    try:
        print("Attempting to send email...")
        # Check the connection to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.quit()
        print("Connection successful!")
        
        # If the connection is successful, send the email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
            return "Email sent successfully!"
        except Exception as e:
            return f"Failed to send email: {e}"
    except smtplib.SMTPAuthenticationError:
        return "Failed to authenticate. Check your username and password."
    except smtplib.SMTPConnectError:
        return "Failed to connect to the SMTP server. Check the server address and port."
    except Exception as e:
        return f"An error occurred: {e}"

