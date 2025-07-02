import requests
import smtplib
import time
import os
import subprocess

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
MONITOR_URL = 'http://54.226.42.105'  # Your app URL

def send_email(subject, body):
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        msg = f"Subject: {subject}\n\n{body}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)
    print("Email Alert Sent")

def restart_container():
    print("Restarting container...")
    subprocess.run(["docker", "restart", "oiia-cat-app"], check=True)

def reboot_server():
    print("Rebooting server...")
    send_email("Server Reboot", f"Server is rebooting because the app is still down: {MONITOR_URL}")
    subprocess.run(["sudo", "reboot"], check=True)

def monitor():
    print("Checking app status...")
    try:
        response = requests.get(MONITOR_URL, timeout=10)
        if response.status_code == 200:
            print("Website is UP")
        else:
            print(f"Unexpected status: {response.status_code}, restarting container...")
            send_email("App Down", f"Status: {response.status_code}, restarting container.")
            restart_container()
            time.sleep(15)
            second_check()
    except:
        print("App unreachable, restarting container...")
        send_email("App Down", "App unreachable, restarting container.")
        restart_container()
        time.sleep(15)
        second_check()

def second_check():
    print("Rechecking app status after restart...")
    try:
        response = requests.get(MONITOR_URL, timeout=10)
        if response.status_code == 200:
            print("App recovered after restart.")
        else:
            print("App still down, rebooting server...")
            reboot_server()
    except:
        print("App unreachable after restart, rebooting server...")
        reboot_server()


print("Monitoring started...")
while True:
    monitor()
    time.sleep(60)
