import glob
import json
import datetime
import os.path
import dateutil.parser

GARMIN_BACKUP_FOLDER = "C:\Users\godin\Projects\garmin-backup"

if __name__ == "__main__":
    for filename in glob.glob(GARMIN_BACKUP_FOLDER + os.path.sep + "201[78]*summary.json"):
        with open(filename) as f:
            data = json.load(f)
            if data['activityTypeDTO']['typeKey'] != 'running':
                continue
            datetime_activity = dateutil.parser.parse(data['summaryDTO']['startTimeGMT'])
            datetime_low = datetime.datetime(2018, 9, 1)
            datetime_high = datetime.datetime(2019, 4, 13)
            if datetime_low <= datetime_activity <= datetime_high:
                print "{0}: {1}".format(datetime_activity, data['summaryDTO']['distance'])
