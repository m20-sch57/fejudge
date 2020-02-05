from flask_mail import Message
from app import app, mail


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


def send_email(subject, sender, recipients, text_body='', html_body=''):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_verification_code(email, name, code):
    send_email(
        subject='Fejudge: verification code',
        sender=app.config['MAIL_USERNAME'],
        recipients=[email],
        text_body=VERIFY_LETTER.format(name, code)
    )


def send_new_password(email, name, password):
    send_email(
        subject='Fejudge: new password',
        sender=app.config['MAIL_USERNAME'],
        recipients=[email],
        text_body=NEW_PASSWORD_LETTER.format(name, password)
    )
