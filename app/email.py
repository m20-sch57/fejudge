import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app import app


VERIFY_LETTER = \
"""
Dear {},

You submitted a request to restore your password.
Here is the code:
{}

Do not share it with anyone!

Yours,
Fejudge team
"""

NEW_PASSWORD_LETTER = \
"""
Dear {},

You tried to restore your password recently.
Your new password is:
{}

Yours,
Fejudge team
"""


def send_email(from_email, to_email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    smtp_server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    smtp_server.starttls()
    smtp_server.login(
        app.config['SYSTEM_EMAIL'],
        app.config['SYSTEM_EMAIL_PASSWORD']
    )
    smtp_server.send_message(msg)


def send_verification_code(email, name, code):
    send_email(
        app.config['SYSTEM_EMAIL'],
        email,
        'Fejudge: verification code',
        VERIFY_LETTER.format(name, code)
    )


def send_new_password(email, name, password):
    send_email(
        app.config['SYSTEM_EMAIL'],
        email,
        'Fejudge: new password',
        NEW_PASSWORD_LETTER.format(name, password)
    )
