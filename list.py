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

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_events(service, calendar_id, start_time, end_time):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def get_busy_times(events):
    busy_times = []
    for event in events:
        start = dateutil.parser.parse(event['start'].get('dateTime'))
        end = dateutil.parser.parse(event['end'].get('dateTime'))
        busy_times.append((start, end))
    busy_times.sort(key=lambda x: x[0])
    return busy_times

def merge_busy_times(busy_times):
    merged_busy_times = [busy_times[0]]
    for current_start, current_end in busy_times[1:]:
        last_end = merged_busy_times[-1][1]
        if current_start <= last_end:
            merged_busy_times[-1] = (merged_busy_times[-1][0], max(last_end, current_end))
        else:
            merged_busy_times.append((current_start, current_end))
    return merged_busy_times

def get_free_slots(merged_busy_times, start_time, end_time, duration):
    free_slots = []
    for i in range(len(merged_busy_times) - 1):
        free_start = merged_busy_times[i][1]
        free_end = merged_busy_times[i + 1][0]
        if free_end > free_start + timedelta(hours=duration):
            free_slots.append((free_start, free_end))
    if start_time + timedelta(hours=duration) <= merged_busy_times[0][0]:
        free_slots.insert(0, (start_time, merged_busy_times[0][0]))
    if end_time >= merged_busy_times[-1][1] + timedelta(hours=duration):
        free_slots.append((merged_busy_times[-1][1], end_time))
    return free_slots

def main():
    date = "2023-07-04"
    duration = 1
    start_time = datetime.strptime(date, '%Y-%m-%d')
    start_time = pytz.utc.localize(start_time)
    end_time = start_time + timedelta(days=1)
    try:
        creds = authenticate()
        service = build('calendar', 'v3', credentials=creds)
        calendar_id = 'primary'
        events = get_events(service, calendar_id, start_time, end_time)
        busy_times = get_busy_times(events)
        merged_busy_times = merge_busy_times(busy_times)
        free_slots = get_free_slots(merged_busy_times, start_time, end_time, duration)
        for slot in free_slots:
            print("Free slot: {} - {} {}".format(slot[0], slot[1], slot[1] - slot[0]))
    except HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
    main()
