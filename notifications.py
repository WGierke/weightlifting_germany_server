import requests
import json
import os
import ConfigParser

if os.path.isfile("config.ini"):
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.ini')
    SLACK_KEY = config.get("slack", "Webhook")

def send_to_slack(text, username="Germany", important=True):
    color = "#ff0000" if important else "#ffffff"
    requests.post(SLACK_KEY, data=json.dumps({"username": username, "attachments": [{"color": color, "text": text}]}))

def notify_users(article):
    # Notify app users
    send_to_slack("New article: " + article["heading"], username=article["publisher"], important=False)
