import time
import imaplib
import email
import os
import requests
import socket
import threading

# نفتح بورت وهمي باش Render يقبل الخدمة
def fake_server():
    s = socket.socket()
    s.bind(('0.0.0.0', int(os.environ.get("PORT", 10000))))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        conn.close()

threading.Thread(target=fake_server, daemon=True).start()

# معلومات من المتغيرات
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# الاتصال بـ Gmail
def connect_to_gmail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_USER, GMAIL_PASSWORD)
    mail.select("inbox")
    return mail

# جلب آخر رسالة
def get_latest_email(mail):
    status, messages = mail.search(None, "UNSEEN")
    if status != "OK":
        return None

    for num in messages[0].split():
        status, data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            continue
        msg = email.message_from_bytes(data[0][1])

        subject = msg["subject"]
        from_ = msg["from"]

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(errors="ignore")
                    except:
                        body = "[غير قابل للقراءة]"
        else:
            try:
                body = msg.get_payload(decode=True).decode(errors="ignore")
            except:
                body = "[غير قابل للقراءة]"

        return f"📧 New Email\nFrom: {from_}\nSubject: {subject}\n\n{body[:500]}"

    return None

# إرسال لتليغرام
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

# حلقة العمل
def main():
    while True:
        try:
            mail = connect_to_gmail()
            message = get_latest_email(mail)
            if message:
                send_to_telegram(message)
            mail.logout()
        except Exception as e:
            print("Error:", e)
        time.sleep(60)

if __name__ == "__main__":
    main()
