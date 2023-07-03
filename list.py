from __future__ import print_function

import os.path
from datetime import datetime, timedelta
import dateutil.parser
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# 予定を探す日付と時間の長さ
DATE = "2023-07-04"  # YYYY-MM-DD形式
DURATION = 1  # 予定の時間の長さ（時間単位）


def get_free_slots():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        # 予定を取得するカレンダーのIDを設定
        calendar_id = 'primary'

        # 指定した日の開始時間と終了時間
        start_time = datetime.strptime(DATE, '%Y-%m-%d')
        start_time = pytz.utc.localize(start_time)
        end_time = start_time + timedelta(days=1)

        # 指定した日の予定を取得
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_time.isoformat(),
            timeMax=end_time.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        busy_times = []
        for event in events:
            start = dateutil.parser.parse(event['start'].get('dateTime'))
            end = dateutil.parser.parse(event['end'].get('dateTime'))
            busy_times.append((start, end))

        # Sort the busy times by their start time
        busy_times.sort(key=lambda x: x[0])

        # Merge overlapping busy times
        merged_busy_times = [busy_times[0]]
        for current_start, current_end in busy_times[1:]:
            last_end = merged_busy_times[-1][1]
            # If the current and last busy times overlap, extend the current busy time
            if current_start <= last_end:
                merged_busy_times[-1] = (merged_busy_times[-1][0], max(last_end, current_end))
            else:
                # Add the current busy time
                merged_busy_times.append((current_start, current_end))

        # Find the free slots
        free_slots = []
        for i in range(len(merged_busy_times) - 1):
            free_start = merged_busy_times[i][1]
            free_end = merged_busy_times[i + 1][0]
            if free_end > free_start + datetime.timedelta(hours=DURATION):
                free_slots.append((free_start, free_end))

        # Check the start of the day
        if start_time + timedelta(hours=DURATION) <= merged_busy_times[0][0]:
            free_slots.insert(0, (start_time, merged_busy_times[0][0]))

        # Check the end of the day
        if end_time >= merged_busy_times[-1][1] + timedelta(hours=DURATION):
            free_slots.append((merged_busy_times[-1][1], end_time))

        return free_slots

    except HttpError as error:
        print('An error occurred: %s' % error)
        return []


def main():
    free_slots = get_free_slots()
    for slot in free_slots:
        print("Free slot: {} - {} {}".format(slot[0], slot[1], slot[1] - slot[0]))



if __name__ == '__main__':
    main()
