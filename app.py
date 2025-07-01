import os
import time
import imaplib
import email
import requests

EMAIL_ACCOUNT = os.environ["GMAIL_USER"]
EMAIL_PASSWORD = os.environ["GMAIL_PASSWORD"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def check_email():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    result, data = mail.search(None, "UNSEEN")
    ids = data[0]
    id_list = ids.split()

    for num in id_list:
        result, data = mail.fetch(num, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = msg["subject"]
        from_ = msg["from"]

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        text = f"📧 New Email\nFrom: {from_}\nSubject: {subject}\n\n{body[:500]}"

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text})

        mail.store(num, '+FLAGS', '\\Seen')

    mail.logout()

if __name__ == "__main__":
    while True:
        check_email()
        time.sleep(60)
