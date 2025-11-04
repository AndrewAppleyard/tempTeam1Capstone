import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# should use Microsoft's Graph API

senderEmail = "spraph00@outlook.com"
password = "your_app_password"
receiverEmail = "spraph00@outlook.com"
attachment  = "/home/user/Downloads/cat.jpg" # would be student schedule that is generated

# use cases: 
#   advisor
#       advising appointments
#       overrides?
#       request to change major/apply for minor?
#   student
#       advising appointments
#       email pdf of confirmed next sem schedule (maybe degree plan as well)
msg = MIMEMultipart("alternative")
msg["Subject"] = "Numa Advising - [Important subject here]" # filtering should be done based on header?
msg["From"] = sender_email
msg["To"] = receiver_email

text = "This is a test email sent from Python running on Linux!"
msg.attach(MIMEText(text, "plain"))
msg.attach(attachment)

with smtplib.SMTP("smtp.office365.com", 587) as server:
    server.starttls() # encrypts connection
    server.login(sender_email, password)
    server.send_message(msg)

print("Email sent successfully!")