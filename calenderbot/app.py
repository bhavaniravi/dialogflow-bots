from flask import Flask, request, jsonify, render_template
from env import CALENDER_ID, AUTH_JSON
import dateparser
from googleapiclient.discovery import build
from google.oauth2 import service_account
import traceback
import os
import datetime

SCOPES = ["https://www.googleapis.com/auth/calendar"]
DELEGATE = "calenderbot@rare-shuttle-106018.iam.gserviceaccount.com"
app = Flask(__name__)


def construct_fullfillment_response(text):
    return {"fulfillmentMessages": [{"text": {"text": [text]}}]}


def get_calendar_service():
    SERVICE_ACCOUNT_FILE = (
        "/Users/venkateshs/bhava/projects/dialogflow-bots/calenderbot/credentials.json"
    )
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    credentials_delegated = credentials.with_subject(DELEGATE)
    service = build("calendar", "v3", credentials=credentials_delegated)
    return service


def create_event(data):
    data = {
        "summary": data["summary"],
        "start": data["start"],
        "end": data["end"],
    }
    """
    data = {
        'summary': 'TinkerHub Workshop',
        'start': {
          'dateTime': '2015-05-28T09:00:00-07:00',
          'timeZone': 'America/Los_Angeles',
        },
        'end': {
          'dateTime': '2015-05-28T17:00:00-07:00',
          'timeZone': 'America/Los_Angeles',
        },
        'attendees': [
          {'email': 'lpage@example.com'},
          {'email': 'sbrin@example.com'},
        ],
      }
    """
    service = get_calendar_service()
    event = service.events().insert(calendarId=CALENDER_ID, body=data).execute()

    return construct_fullfillment_response(
        "Event created: %s" % (event.get("htmlLink"))
    )


def call_calender_action(data):
    data["summary"] = data["task"]
    data["start"] = {
        "dateTime": data["date-time"],
        "timeZone": "Asia/Calcutta",
    }
    now_30_mins = datetime.datetime.now() + datetime.timedelta(minutes=30)
    data["end"] = {
        "dateTime": now_30_mins.strftime("%Y-%m-%d:%H:%M:%S+05:30"),
        "timeZone": "Asia/Calcutta",
    }
    create_event(data)


class UnsupportedActionException(Exception):
    pass


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    action = data["queryResult"]["action"]
    try:
        if action == "schedule":
            return jsonify(call_calender_action(data["queryResult"]["parameters"]))
        else:
            raise UnsupportedActionException("Invalid action")

    except UnsupportedActionException as e:
        traceback.print_exc(e)
        return jsonify(construct_fullfillment_response(repr(e)))


if __name__ == "__main__":
    app.run(debug=True)
