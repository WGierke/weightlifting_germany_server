#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
from collections import Counter
from tabulate import tabulate
import requests
import json
import ConfigParser

def send_get_api_request(url, secret_key):
    return requests.get(url, headers={"Content-Type": "application/json", "X-Secret-Key": secret_key}).content


config = ConfigParser.RawConfigParser(allow_no_value=True)
config.read('config.ini')
secret_key = config.get("appspot", "X-Secret-Key")

filter_responses = send_get_api_request("http://weightliftinggermany.appspot.com/get_protocols", secret_key)
filter_objects = json.loads(filter_responses)["result"]

shares = []
for obj in filter_objects:
    competition_parties = obj["parties"]
    shares.append(competition_parties)

print "Collected " + str(len(shares)) + " shared protocols:"
shares = Counter(shares).most_common()
shares.insert(0, ('Share', 'Count'))
print tabulate(shares)
