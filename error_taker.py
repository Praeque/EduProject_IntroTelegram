import json
import datetime
from pytz import timezone

ukraine_time = timezone('Europe/Kiev')


def save_error(error):
    with open('data/errors.json', 'r') as file_errors:
        data_errors = json.load(file_errors)
    ua_time_now = datetime.datetime.now(ukraine_time)
    now_day = ua_time_now.date().day
    now_month = ua_time_now.date().month
    now_year = ua_time_now.date().year
    now_hour = ua_time_now.time().hour
    now_minute = ua_time_now.time().minute
    new_error = f'{error} |***|     {(now_hour < 9) * "0" + str(now_hour)}:{(now_minute < 9) * "0" + str(now_minute)}' \
                f'      {(now_day < 9)*"0"+str(now_day)}.{(now_month < 9)*"0"+str(now_month)}.{now_year}'
    data_errors.append(new_error)
    with open('data/errors.json', 'w') as file_errors:
        json.dump(data_errors, file_errors, indent=4)


