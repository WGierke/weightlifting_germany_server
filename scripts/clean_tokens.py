#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
from gcm import GCM
import requests
import json
import ConfigParser

def send_appspot_get_request(url, secret_key):
    return requests.get("http://weightliftinggermany.appspot.com/" + url, headers={"Content-Type": "application/json", "X-Secret-Key": secret_key}).content


def send_appspot_delete_request(url, secret_key, data):
    return requests.post("http://weightliftinggermany.appspot.com/" + url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded", "X-Secret-Key": secret_key}).content


config = ConfigParser.RawConfigParser(allow_no_value=True)
config.read('config.ini')

gcm_key = config.get("gcm", "API-Key")
secret_key = config.get("appspot", "X-Secret-Key")

push_messages = ["#0#0#0#0#0#0#0"]

gcm = GCM(gcm_key)

appspot_response = send_appspot_get_request("get_tokens", secret_key)
appspot_tokens = json.loads(appspot_response)["result"]
print "Fetched " + str(len(appspot_tokens)) + " tokens"

for line in push_messages:
    data = {'update': line.decode('utf-8')}
    sent_requests = 0
    receivers = []
    for appspot_token in appspot_tokens:
        if appspot_token not in receivers:
            gcm_push_response = gcm.json_request(registration_ids=[appspot_token], data=data)
            if bool(gcm_push_response):
                print appspot_token + " is invalid. Sending request to remove it."
                send_appspot_delete_request("delete_token", secret_key, "token=" + appspot_token)
            else:
                print "Sent " + line.decode('utf-8') + " to " + appspot_token
                receivers.append(appspot_token)
                sent_requests += 1

print "Sent to " + str(sent_requests) + " receivers"