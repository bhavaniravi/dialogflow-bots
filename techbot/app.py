from flask import Flask, jsonify, request
import csv

app = Flask(__name__)


def construct_fullfillment_response(text):
    return {"fulfillmentMessages": [{"text": {"text": [text]}}]}


def get_event(data):
    csvfile = open("events.csv")
    rows = csv.reader(csvfile, delimiter=",")

    tech = data["tech"]
    type_of_event = data["type_of_event"]

    for row in rows:
        if row[5] == type_of_event and tech == row[1]:
            return construct_fullfillment_response(" ".join(row))

    return construct_fullfillment_response("Cannot find an event")


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    action = data["queryResult"]["action"]
    action_data = data["queryResult"]["parameters"]
    if action == "get_event":
        return jsonify(get_event(action_data))
    else:
        return construct_fullfillment_response("action not supported")
    return {"message": "Hello"}


if __name__ == "__main__":
    app.run(debug=True)