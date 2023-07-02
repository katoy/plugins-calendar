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

        free_slots = []
        start_time = start_time
        for event in events:
            end = dateutil.parser.parse(event['end'].get('dateTime'))
            if (end - start_time).total_seconds() / 3600 >= DURATION:
                free_slots.append((start_time, end))
            start_time = dateutil.parser.parse(event['start'].get('dateTime'))

        if (end_time - start_time).total_seconds() / 3600 >= DURATION:
            free_slots.append((start_time, end_time))

        return free_slots

    except HttpError as error:
        print('An error occurred: %s' % error)
        return []


def main():
    free_slots = get_free_slots()
    for slot in free_slots:
        print("Free slot:", slot[0], " - ", slot[1], slot[1] - slot[0])


if __name__ == '__main__':
    main()
