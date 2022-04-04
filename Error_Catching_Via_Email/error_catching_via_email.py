"""
Filename:
    error_catching_via_email.py

Description:
    This is a template that can be used to catch errors via email for the purposes of automating a task or other
    use cases.

Author(s):
    Jonathan Jang
"""


import re
import os
import smtplib
from email.mime.text import MIMEText


def send_error_email(subject, body):
    """
    Function to send email when the program terminates due to error or if an update needs to be send out

    :param subject: str
        String that will be used as the subject for the email that gets sent out for errors or status updates
    :param body: str
        String that will be used as the body for the email that gets sent out for errors or status updates

    :return:
        None
    """
    email_address = "_ENTER_YOUR_EMAIL_HERE_"
    password = "_ENTER_YOUR_PASSWORD_HERE_"
    recipient_email = "_ENTER_RECIPIENT_EMAIL_HERE_,_ENTER_RECIPIENT_2_EMAIL_HERE_"

    if "\n" in body:
        body = re.sub("\n", "<br>", body)
    if "\t" in body:
        body = re.sub("\t", "    ", body)

    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = recipient_email

    # Connection to Gmail SMTP Server
    mail_object = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
    mail_object.login(user=email_address, password=password)
    mail_object.sendmail(email_address, recipient_email.split(","), msg.as_string())
    mail_object.quit()


def other_functions():
    """
        Where the actual code of your project begins
    """
    pass


def main():
    # This will automatically send an error email if run in this state
    #   due to the incorrect function call of other_functions()
    try:
        print("This is the try")
        other_functionsd()

    except Exception as err:
        # if we run into an error, an error email will get sent out and the program will terminate

        script_name = os.path.basename(__file__)
        send_error_email("Please rerun " + script_name + ". It has run into an Error",
                         "Please rerun " + script_name + ". It has run into an Error. \n Error Message is: \n\n" +
                         str(err))
        print(f"\n.\n.\n.\n.\n{script_name} has an ERROR, Email has been sent!")


if __name__ == '__main__':
    main()
