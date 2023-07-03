import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def get_events(service, maxResults=10):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=maxResults, singleEvents=True,
        orderBy='startTime').execute()
    return events_result.get('items', [])


def print_events(events):
    if not events:
        print('No upcoming events found.')
        return

    for event in events:
        start_at = event['start'].get(
            'dateTime', event['start'].get('date'))
        end_at = event['end'].get('dateTime', event['end'].get('date'))
        print("{} - {} '{}'".format(start_at, end_at, event.get('summary', '')))


def main():
    try:
        maxResults = 5
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        print('Getting the upcoming {} events'.format(maxResults))
        events = get_events(service, maxResults)
        print_events(events)
    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
