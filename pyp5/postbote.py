"""
Simple function for sending mail message.

Author: Philipp Buchinger <buchinger@proton.me>
"""

import ssl
from email.utils import formataddr
from email.message import EmailMessage
import smtplib


def send(receiver, subject, content) -> str:
    """send notifications via mail"""
    port = 587  # For starttls
    smtp = ""
    sender = ""
    sender_name = ""
    password = ""

    msg = EmailMessage()
    msg["From"] = formataddr((f"{sender_name}", f"{sender}"))
    msg["To"] = receiver
    msg["Subject"] = f"{subject}"
    msg.set_content(content)

    context = ssl.create_default_context()

    with smtplib.SMTP(smtp, port) as server:
        try:
            # server.set_debuglevel(1)
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            return "Mail sent."
        except smtplib.SMTPException as error:
            return str(error)
