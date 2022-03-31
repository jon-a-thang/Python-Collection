"""
Filename:
    send_attachment_email.py

Description:
    This project is where someone will be able to send an email a desired recipient with an attachment
    
    When sending out the attachment in an email, the program will create a zip of the folder or the file that
    is going to be send out to the recipients

Author(s):
    Jonathan Jang
"""
import shutil
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_attachment_email(subject, body):
    """
    Function to send out an email with an attachment that the program will zip
    
    :param subject: str
        String that will be used as the subject for the email
    :param body: str
        String that will be used as the body for the email
    :return:
        None
    """
    
    # Making a zip file to send out in the email
    dir_name = "LOCATION_OF_FILES_OR_FOLDER_TO_SEND_OUT"
    output_filename = "ZIP_FILE_NAME"
    shutil.make_archive(output_filename, 'zip', dir_name)
    zip_filename = output_filename + ".zip"
    
    # Getting the required information in order to send emails
    fromaddr = "SENDER_EMAIL"
    password = "PASSWORD_OF_FROMADDR"
    toaddr = "RECIPIENT_EMAIL_ADDRESS_1, RECIPIENT_EMAIL_ADDRESS_2"

    try:
        msg = MIMEMultipart()

        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Sending the zipped report via email
        attachment = open(zip_filename, "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % zip_filename)

        msg.attach(part)
        
        # Connection to Gmail SMTP Server over port 465 (SSL)
        mail_object = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        mail_object.login(fromaddr, password)
        text = msg.as_string()
        mail_object.sendmail(fromaddr, toaddr.split(","), text)
        mail_object.quit()
        
        print("Successfully send the email!")
    
    except smtplib.SMTPSenderRefused:
        print("\n\nFailed to send the email....attachment size is too large")


if __name__ == '__main__':
    send_attachment_email("_ENTER_SUBJECT_LINE_OF_EMAIL_", "_ENTER_BODY_OF_EMAIL_")
