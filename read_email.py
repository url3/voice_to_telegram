import imaplib
import email
from email.header import decode_header
import time
import requests
from datetime import datetime
import os

def parse_email_date(email_date):
    parsed_date = email.utils.parsedate(email_date)
    if parsed_date is not None:
        return time.mktime(parsed_date)
    return 0  # 返回一个最小值以避免比较时出错

def read_emails(gmail_user, gmail_password, telegram_token, telegram_chat_id):
    # Connect to Gmail IMAP server
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(gmail_user, gmail_password)
    mail.select('inbox')

    # Load last checked time
    try:
        with open('last_checked.txt', 'r') as f:
            last_checked = f.read().strip()
    except FileNotFoundError:
        last_checked = '1970-01-01 00:00:00'

    last_checked_time = parse_email_date(last_checked)

    # Fetch latest emails
    result, data = mail.search(None, 'ALL')
    email_ids = data[0].split()[-10:]  # Get latest 10 emails

    for e_id in email_ids:
        result, msg_data = mail.fetch(e_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        email_date = msg['Date']
        email_subject, encoding = decode_header(msg['Subject'])[0]

        if isinstance(email_subject, bytes):
            email_subject = email_subject.decode(encoding if encoding else 'utf-8')

        email_time = parse_email_date(email_date)

        if email_time > last_checked_time and '新短信' in email_subject:
            email_body = msg.get_payload(decode=True).decode()
            # Send to Telegram
            message = f"{email_date} - {email_subject}\n{email_body}"
            requests.post(f"https://api.telegram.org/bot{telegram_token}/sendMessage", data={"chat_id": telegram_chat_id, "text": message})

    # Update last checked time
    with open('last_checked.txt', 'w') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    GMAIL_USER = os.environ['GMAIL_USER']
    GMAIL_PASSWORD = os.environ['GMAIL_PASSWORD']
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

    read_emails(GMAIL_USER, GMAIL_PASSWORD, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
