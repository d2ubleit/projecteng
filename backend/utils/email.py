import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.database.config import SMTP_PASSWORD,SMTP_PORT,SMTP_SERVER,SMTP_USER

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)