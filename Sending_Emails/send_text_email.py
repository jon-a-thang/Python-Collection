"""
Filename:
    send_text_email.py

Description:
    This project is where someone will be able to send an email a desired recipient.

    Note: This will only work with text-based emails.

Author(s):
    Jonathan Jang
"""
import re
import smtplib
from email.mime.text import MIMEText


def send_text_email(subject, body):
    """
    Function to send an email

    :param subject: str
        String that will be used as the subject for the email
    :param body: str
        String that will be used as the body for the email

    :return:
        None
    """
    email_address = "_ENTER_FROM_EMAIL_HERE_"
    recipient_email = "_ENTER_TO_EMAIL_HERE_"

    if "\n" in body:
        body = re.sub("\n", "<br>", body)
    if "\t" in body:
        body = re.sub("\t", "    ", body)

    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = recipient_email

    # Connection to Gmail SMTP Server over port 465 (SSL)
    mail_object = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
    mail_object.login(user=email_address, password='_ENTER_PASSWORD_OF_FROM_EMAIL_HERE_')
    mail_object.sendmail(email_address, recipient_email.split(","), msg.as_string())
    mail_object.quit()


if __name__ == '__main__':
    send_text_email("_ENTER_SUBJECT_LINE_OF_EMAIL_", "_ENTER_BODY_OF_EMAIL_")
