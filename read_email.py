import imaplib
import email
import requests
import os
from datetime import datetime, timedelta

def send_to_telegram(message):
    bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={'chat_id': chat_id, 'text': message})

def main():
    user = os.environ['GMAIL_USER']
    password = os.environ['GMAIL_PASS']
    
    # 连接到 Gmail
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(user, password)
    mail.select('inbox')

    # 获取上次记录的时间
    try:
        with open('time.txt', 'r') as f:
            since_time_str = f.read().strip()
            since_time = datetime.strptime(since_time_str, '%a %b %d %H:%M:%S %Z %Y')
    except FileNotFoundError:
        since_time = datetime.now() - timedelta(days=1)  # 默认获取过去一天的邮件

    # 查找邮件
    result, data = mail.search(None, f'(SINCE "{since_time.strftime("%d-%b-%Y")}")')
    email_ids = data[0].split()[-10:]  # 取最新10封邮件

    for e_id in email_ids:
        result, msg_data = mail.fetch(e_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        
        # 提取邮件信息
        date = msg['Date']
        subject = msg['Subject']
        body = ''
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode()
        else:
            body = msg.get_payload(decode=True).decode()
        
        # 创建消息
        message = f"时间: {date}\n标题: {subject}"
        
        # 打印到控制台
        print(message)
        
        # 发送到 Telegram
        send_to_telegram(message)

    # 记录当前时间
    with open('time.txt', 'w') as f:
        f.write(datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y'))

    mail.logout()

if __name__ == "__main__":
    main()
