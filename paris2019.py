import glob
import json
import datetime
import subprocess
import smtplib
import os
import os.path
import dateutil.parser

from PIL import Image, ImageFont, ImageDraw
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CREDENTIALS_FILE = "credentials.json"
PROCESSED_DATES = "processed_dates.txt"
OUTPUT_IMAGE = "output.jpg"
GARMIN_BACKUP_PYTHON = "C:\Python27\python.exe"
GARMIN_BACKUP_FOLDER = "C:\Users\godin\Projects\garmin-backup"
GARMIN_BACKUP_SCRIPT = "C:\Users\godin\Projects\garminexport\garminbackup.py"
PREPARATION_TITLE = 'Paris Marathon'
PREPARATION_GOAL = 1000  # kilometers
PREPARATION_START = datetime.datetime(2018, 9, 1)
PREPARATION_END = datetime.datetime(2019, 4, 1)


def update_activities():
    with open(CREDENTIALS_FILE) as credentials_file:
        credentials = json.load(credentials_file)
        print subprocess.check_output([GARMIN_BACKUP_PYTHON,
                                       GARMIN_BACKUP_SCRIPT,
                                       '--password=' + credentials['garmin']['password'],
                                       '--backup-dir=' + GARMIN_BACKUP_FOLDER,
                                       credentials['garmin']['username']],
                                      stderr=subprocess.STDOUT,
                                      universal_newlines=True)


def get_kilometers_done(preparation_start, preparation_end):
    kilometers = 0
    for filename in glob.glob(GARMIN_BACKUP_FOLDER + os.path.sep + "201[89]*summary.json"):
        with open(filename) as f:
            data = json.load(f)
            if data['activityTypeDTO']['typeKey'] != 'running':
                continue
            datetime_activity = dateutil.parser.parse(data['summaryDTO']['startTimeGMT'])
            if preparation_start <= datetime_activity <= preparation_end:
                activity_kilometers = data['summaryDTO']['distance'] / 1000
                kilometers += activity_kilometers
    return kilometers


def create_image(text):
    img = Image.new('RGB', (450, 100), "white")
    draw = ImageDraw.Draw(img)
    draw.text((35, 35),
              text,
              font=ImageFont.truetype("arial", 20),
              fill="red")
    img.save(OUTPUT_IMAGE, "JPEG")


def send_mail(subject, text):
    with open(CREDENTIALS_FILE) as credentials_file:
        credentials = json.load(credentials_file)
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = credentials['mail']['username']
        msg['To'] = credentials['mail']['username']
        msg_text = MIMEText('<b>%s</b><br><img src="cid:%s"><br>' % (text, OUTPUT_IMAGE), 'html')
        msg.attach(msg_text)
        with open(OUTPUT_IMAGE, 'rb') as jpeg:
            img = MIMEImage(jpeg.read())
            img.add_header('Content-ID', '<{}>'.format(OUTPUT_IMAGE))
            msg.attach(img)
        s = smtplib.SMTP(timeout=30)
        s.connect(credentials['mail']['smtphost'])
        try:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(credentials['mail']['username'], credentials['mail']['password'])
            s.sendmail(credentials['mail']['username'], credentials['mail']['username'], msg.as_string())
        finally:
            s.quit()


def is_processed_today():
    dates = set()
    if not os.path.isfile(PROCESSED_DATES):
        return False
    with open(PROCESSED_DATES, 'r') as f:
        for line in f:
            dates.add(dateutil.parser.parse(line).date())
    today = datetime.date.today()
    return today in dates


def set_processed_today():
    with open(PROCESSED_DATES, 'a') as f:
        f.write(str(datetime.date.today()))
        f.write('\n')


if __name__ == "__main__":
    if not is_processed_today():
        update_activities()
        remaining_kilometers = PREPARATION_GOAL - get_kilometers_done(PREPARATION_START, PREPARATION_END)
        remaining_days = (PREPARATION_END - datetime.datetime.now()).days
        per_month_remaining = remaining_kilometers / remaining_days * 30.0
        status_text = "{0} kilometers remaining ({1} per month)".format(int(round(remaining_kilometers)),
                                                                        int(round(per_month_remaining)))
        remaining_text = PREPARATION_TITLE + ": {0} days remaining".format(remaining_days)
        create_image(status_text)
        send_mail(remaining_text, status_text)
        set_processed_today()
