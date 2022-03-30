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
from email.header import decode_header
import webbrowser
import os
import re
import html2text
