import requests
from bs4 import BeautifulSoup
import time
import schedule
import smtplib
from email.mime.text import MIMEText

# === CONFIGURATION ===
JOB_URL = "https://www.wellsfargojobs.com/en/jobs/?search=&country=India&location=BENGALURU&location=HYDERABAD&team=Product+Management&team=Strategy+%26+Execution&type=Full+time"
KEYWORDS = ["Digital Product Manager", "Lead Business Consultant", "Project Manager"]

TELEGRAM_BOT_TOKEN = "7561360738:AAE1Stxz8NX5YbyHri85mJdvt6C1d0AR2aM"
TELEGRAM_CHAT_ID = "977567779"

EMAIL_ADDRESS = "ashish.panda90@gmail.com"
EMAIL_APP_PASSWORD = "gegqoheupeexdnia"
EMAIL_TO = "ashish.panda90@gmail.com"

# === TRACKING NEW JOBS ===
seen_jobs = set()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

def send_email_alert(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_TO, msg.as_string())

def fetch_jobs():
    global seen_jobs
    new_jobs_found = False

    for page in range(1, 5):  # Check first 4 pages
        url = f"{JOB_URL}&page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.find_all("a", class_="job-title-link")

        for card in job_cards:
            title = card.text.strip()
            link = "https://www.wellsfargojobs.com" + card.get("href")

            if any(kw.lower() in title.lower() for kw in KEYWORDS) and link not in seen_jobs:
                seen_jobs.add(link)
                new_jobs_found = True

                message = f"🆕 New Job Posted!\n\nTitle: {title}\nLink: {link}"
                send_telegram_alert(message)
                send_email_alert("New Wells Fargo Job Alert", message)

    if not new_jobs_found:
        print("✅ Checked: No new jobs found.")

# === SCHEDULING ===
print("🔁 Job monitor started. Checking every 15 minutes...")
schedule.every(15).minutes.do(fetch_jobs)

while True:
    schedule.run_pending()
    time.sleep(5)
