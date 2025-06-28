import requests
import smtplib
import time
import os
from dotenv import load_dotenv
import schedule
import subprocess

load_dotenv()

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
MONITOR_URL = 'http://54.226.42.105'  # Replace with your actual app URL

def send_email(subject, body):
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        msg = f"Subject: {subject}\n\n{body}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)
    print("Alert Email Sent!")

def restart_container():
    print("Restarting Cat Page Container...")
    subprocess.run(["docker", "restart", "oiia-cat-app"], check=True)

def restart_server():
    print("Rebooting server...")
    send_email("Server Reboot Triggered", f"The server is being rebooted as the app remains down: {MONITOR_URL}")
    subprocess.run(["sudo", "reboot"], check=True)

def monitor():
    try:
        response = requests.get(MONITOR_URL, timeout=10)
        if response.status_code == 200:
            print("Oiia Cat Website is UP!")
        else:
            print(f"Unexpected Status: {response.status_code}")
            send_email("Oiia Cat Website DOWN", f"Status: {response.status_code}. Attempting restart.")
            restart_container()
            time.sleep(15)
            recheck()
    except Exception as e:
        print(f"Website Down: {e}")
        send_email("Oiia Cat Website DOWN", f"Error: {e}. Attempting restart.")
        restart_container()
        time.sleep(15)
        recheck()

def recheck():
    try:
        response = requests.get(MONITOR_URL, timeout=10)
        if response.status_code == 200:
            print("App recovered after restart.")
        else:
            print("App still down. Rebooting server.")
            restart_server()
    except:
        print("App unreachable after restart. Rebooting server.")
        restart_server()

# Run every 1 minute
schedule.every(1).minutes.do(monitor)

print("Monitoring Started...")

monitor()

while True:
    schedule.run_pending()
    time.sleep(1)

