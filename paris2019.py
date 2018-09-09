import glob
import json
import datetime
import subprocess
import os
import os.path
import dateutil.parser

GARMIN_CREDENTIALS_FILE = "credentials.json"
GARMIN_BACKUP_PYTHON = "C:\Python27\python.exe"
GARMIN_BACKUP_FOLDER = "C:\Users\godin\Projects\garmin-backup"
GARMIN_BACKUP_SCRIPT = "C:\Users\godin\Projects\garminexport\garminbackup.py"
PREPARATION_GOAL = 1000  # kilometers
PREPARATION_START = datetime.datetime(2018, 9, 1)
PREPARATION_END = datetime.datetime(2019, 4, 1)


def update_activities():
    with open(GARMIN_CREDENTIALS_FILE) as f:
        credentials = json.load(f)
        print subprocess.check_output([GARMIN_BACKUP_PYTHON,
                                       GARMIN_BACKUP_SCRIPT,
                                       '--password=' + credentials['password'],
                                       '--backup-dir=' + GARMIN_BACKUP_FOLDER,
                                       credentials['username']],
                                      stderr=subprocess.STDOUT,
                                      universal_newlines=True)


def get_remaining_kilometers():
    kilometers = PREPARATION_GOAL
    for filename in glob.glob(GARMIN_BACKUP_FOLDER + os.path.sep + "201[89]*summary.json"):
        with open(filename) as f:
            data = json.load(f)
            if data['activityTypeDTO']['typeKey'] != 'running':
                continue
            datetime_activity = dateutil.parser.parse(data['summaryDTO']['startTimeGMT'])
            if PREPARATION_START <= datetime_activity <= PREPARATION_END:
                activity_kilometers = data['summaryDTO']['distance'] / 1000
                kilometers -= activity_kilometers
    return kilometers


if __name__ == "__main__":
    update_activities()
    remaining_kilometers = get_remaining_kilometers()
    remaining_days = (PREPARATION_END - datetime.datetime.now()).days
    per_month_remaining = remaining_kilometers / remaining_days * 30.0
    print "{0} kilometers remaining ({1} per month)".format(int(round(remaining_kilometers)),
                                                            int(round(per_month_remaining)))
