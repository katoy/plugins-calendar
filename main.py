import os.path
import datetime
import json
import requests
import urllib.parse

import quart
import quart_cors
from quart import request, jsonify

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Constants
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
ALLOWED_ORIGIN = "https://chat.openai.com"
APP_DEBUG = True
APP_HOST = "0.0.0.0"
APP_PORT = 5003
TOKENS_PATH = "./tokens"
MAX_EVENTS = 10

# App setup
app = quart_cors.cors(quart.Quart(__name__), allow_origin=ALLOWED_ORIGIN)


def get_user_id():
    return request.headers.get('X-PluginLab-User-Id')


def get_bearer_token():
    auth_header = request.headers.get('Authorization')
    return auth_header.replace('Bearer ', '', 1) if auth_header else ''


def build_service(user_id):
    creds = None
    json_name = os.path.join(TOKENS_PATH, f"{user_id}.json")

    if os.path.exists(json_name):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(json_name, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def get_events(service, maxResults=MAX_EVENTS):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=maxResults, singleEvents=True,
        orderBy='startTime').execute()
    return events_result.get('items', [])


def format_events(events):
    if not events:
        return ['No upcoming events found.']

    formatted_events = []
    for event in events:
        start_at = event['start'].get(
            'dateTime', event['start'].get('date'))
        end_at = event['end'].get('dateTime', event['end'].get('date'))
        formatted_events.append(
            f"{start_at} - {end_at} '{event.get('summary', '')}'")
    return formatted_events


@app.route('/events', methods=['GET'])
async def events():
    try:
        user_id = get_user_id()
        service = build_service(user_id)
        events = get_events(service)
        formatted_events = format_events(events)
        return {"items": formatted_events }, 200
    except HttpError as error:
        print(f'An error occurred: {error}')
        return jsonify({"error": str(error)}), 400


@app.get("/logout")
async def logout():
    user_id = get_user_id()
    json_name = os.path.join(TOKENS_PATH, f"{user_id}.json")
    if os.path.exists(json_name):
        os.remove(json_name)
    return {}, 200


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open(".well-known/ai-plugin.json") as f:
        text = f.read()
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/yaml")


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


def main():
    app.run(debug=APP_DEBUG, host=APP_HOST, port=APP_PORT)


if __name__ == "__main__":
    main()
