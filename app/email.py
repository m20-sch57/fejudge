from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app import app, smtp_server


def send_email(from_email, to_email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    smtp_server.send_message(msg)


def send_verification_code(email, code):
    send_email(
        app.config['SYSTEM_EMAIL'],
        email,
        'Fejudge: verification code',
        """
        Hello!
        Here is the code to restore your password:
        {}

        Do not share it with anyone!

        Fejudge team
        """.format(code)
    )


def send_new_password(email, password):
    send_email(
        app.config['SYSTEM_EMAIL'],
        email,
        'Fejudge: new password',
        """
        Hello!

        Your new password is:
        {}

        Fejudge team
        """.format(password)
    )
