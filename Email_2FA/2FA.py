"""
Filename:
    2FA.py

Description:
    Email 2FA Authentication Code Grabber

Author(s):
    Jonathan Jang
"""
import imaplib
import email
import re
import html2text


def get_inbox(subject_line, sender):
    """
    get_inbox will get the entire inbox and search through them to look for emails that contain the subject line and sender that we are looking for
    
    :param subject_line: str
        The subject line of the email that we are looking for
    :param sender: str
        The email address of where the code gets sent from
    
    :return:
        list of emails that could contain the 2FA code
    """
    # account credentials
    username = "ENTER_EMAIL_HERE"
    password = "ENTER_PASSWORD_HERE"

    # create an IMAP4 class with SSL
    imap_mail = imaplib.IMAP4_SSL("imap.gmail.com")
    
    # authenticating the email 
    imap_mail.login(username, password)
    imap_mail.select("inbox")
    tmp, search_data = imap_mail.search(None, 'ALL')
    # print(search_data)
    
    # the list that gets returned with the emails that have the subject line and sender that we are looking for
    list_of_emails = []
    
    for num in search_data[0].split():
        email_data = {}
        tmp, data = imap_mail.fetch(num, '(RFC822)')
        # print(data[0])
        tmp, b = data[0]
        email_message = email.message_from_bytes(b)
        for header in ['subject', 'to', 'from', 'date']:
            # print("{}: {}".format(header, email_message[header]))
            email_data[header] = email_message[header]
        # if "ENTER_SUBJECT_HERE" in email_data["subject"] and "ENTER_FROM_EMAIL_HERE" in email_data["from"]:
        if subject_line in email_data["subject"] and sender in email_data["from"]:
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True)
                    email_data['body'] = body.decode()
                    # print(email_data['body'])
                elif part.get_content_type() == "text/html":
                    html_body = part.get_payload(decode=True)
                    email_data['html_body'] = html_body.decode()
                    # print(email_data['html_body'])
            list_of_emails.append(email_data)
        # print(email_data)
       
    return list_of_emails


def get_mfa_code(subject_line, sender):
    """
    get_mfa_code will get a list of emails that could contain the 2FA authentication code and then return that information
    
    :param subject_line: str
        The subject line of the email that we are looking for
    :param sender: str
        The email address of where the code gets sent from
    
    :return:
        list of possible 2FA codes
    """
    inbox = get_inbox(subject_line, sender)
    otp_list = []
    for each in inbox:
        # print(each["subject"])
        try:
            otp = re.search("[0-9][0-9][0-9][0-9][0-9][0-9]", each["body"])
            # print(each["body"])
            otp_list.append(otp[0])
        except KeyError:
            otp = re.search("[\n][0-9][0-9][0-9][0-9][0-9][0-9]", html2text.html2text(each["html_body"]))
            # print(html2text.html2text(each["html_body"]))
            otp_list.append(otp[0].strip())
        print(otp[0])
    print(otp_list)
    return otp_list


def main():
    """
    Main function to run Email 2FA Code Grabber

    :return:
        None
    """
    # EMAIL 2FA CODE GRABBER
    get_mfa_code("ENTER_SUBJECT_LINE_HERE", "ENTER_FROM_EMAIL_HERE")

    
if __name__ == '__main__':
    main()
