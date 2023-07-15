import datetime
import os.path

import json
import requests
import urllib.parse
import datetime

import quart
import quart_cors
from quart import request
from quart import jsonify

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Note: Setting CORS to allow chat.openapi.com is only required when running a localhost plugin
app = quart_cors.cors(quart.Quart(__name__),
                      allow_origin="https://chat.openai.com")

@app.route('/events', methods=['GET'])
async def events():
    # リクエストヘッダーからaccess_tokenを取得
    token = ''
    try:
        bearer_token = get_bearer_token(request)
    except IndexError:
        return jsonify({"error": "Bearer token not found in Authorization header"}), 400

    if bearer_token == '':
        return jsonify({"error": "Authorization header not found"}), 400

    try:
        maxResults = 5
        creds = get_credentials(get_user_id(request))
        service = build('calendar', 'v3', credentials=creds)
        print('Getting the upcoming {} events'.format(maxResults))
        events = get_events(service, maxResults)
        print_events(events)
        return {"items": events }, 200
    except HttpError as error:
        print(f'An error occurred: {error}')
        return jsonify({"error": error}), 400


@app.get("/logout")
async def logout():
    user_id = get_user_id(request)
    json_name = "./tokens/{}.json".format(user_id)
    if os.path.exists(json_name):
        os.remove(json_name)
    return {}, 200


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open(".well-known/ai-plugin.json") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the manifest
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/yaml")


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

def get_bearer_token(request):
    print("----------------")
    print(request.headers)
    auth_header = request.headers.get('Authorization')
    print("[" + auth_header + "]")
    if auth_header:
        auth_header.replace('Bearer ', '', 1)
        return auth_header

    return ''


def get_user_id(request):
    user_id = request.headers.get('X-PluginLab-User-Id')
    print("userod: [" + user_id + "]")
    return user_id


def get_credentials(user_id):
    creds = None
    json_name = "./tokens/{}.json".format(user_id)

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
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
