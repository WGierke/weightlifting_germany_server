#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
from collections import Counter
from tabulate import tabulate
import requests
import json
import ConfigParser

def send_parse_api_request(method, url, app_id, rest_key):
    request_method = getattr(requests, method)
    response = request_method(url, headers={"Content-Type": "application/json", "X-Parse-Application-Id": app_id, "X-Parse-REST-API-Key": rest_key}).content
    return response

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.read('config.ini')
application_id = config.get("parse", "X-Parse-Application-Id")
rest_key = config.get("parse", "X-Parse-REST-API-Key")

filter_responses = send_parse_api_request("get", "https://api.parse.com/1/classes/FilterSetting?limit=999", application_id, rest_key)
filter_objects = json.loads(filter_responses)["results"]
ordered_objects = list(reversed(filter_objects))

seen = []
filters = []
for obj in ordered_objects:
    user_id = obj["userId"]
    filter_setting = obj["filter"]
    if user_id not in seen:
        seen.append(user_id)
        filters.append(filter_setting)
    else:
        print "Sending request to remove outdated filter setting of user " + user_id
        send_parse_api_request("delete", "https://api.parse.com/1/classes/FilterSetting/" + obj["objectId"], application_id, rest_key)

print "Collected " + str(len(filters)) + " filter settings:"
filters = Counter(filters).most_common()
filters.insert(0, ('Filter', 'Count'))
print tabulate(filters)

# ---------------------------------------------------------------------------------------------------------------------------------


def send_get_api_request(url, secret_key):
    return requests.get(url, headers={"Content-Type": "application/json", "X-Secret-Key": secret_key}).content


def send_delete_api_request(url, secret_key, data):
    return requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded", "X-Secret-Key": secret_key}).content


config = ConfigParser.RawConfigParser(allow_no_value=True)
config.read('config.ini')
secret_key = config.get("appspot", "X-Secret-Key")

filter_responses = send_get_api_request("http://weightliftinggermany.appspot.com/get_filters", secret_key)
filter_objects = json.loads(filter_responses)["result"]

ordered_objects = reversed(sorted(filter_objects, key=lambda k: k['createdAt']))

seen = []
filters = []
for obj in ordered_objects:
    user_id = obj["userId"]
    filter_setting = obj["filterSetting"]
    created_at = obj["createdAt"]
    if user_id not in seen:
        seen.append(user_id)
        filters.append(filter_setting)
    else:
        print "Remove user " + user_id + " with setting '" + filter_setting + "' and time stamp " + created_at
        send_delete_api_request("http://weightliftinggermany.appspot.com/delete_filter", secret_key, "userId={}&filterSetting={}".format(user_id, filter_setting))

print "Collected " + str(len(filters)) + " filter settings:"
filters = Counter(filters).most_common()
filters.insert(0, ('Filter', 'Count'))
print tabulate(filters)
