#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import codecs
import ConfigParser
import json
import os
import requests
import subprocess
import urllib2
import yaml

from collections import Counter
from gcm import GCM
from datetime import datetime
from tabulate import tabulate

NEWS_FILE = "news.txt"

if os.path.isfile("config.ini"):
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.ini')
    SLACK_KEY = config.get("slack", "Webhook")
    APPLICATION_ID = config.get("parse", "X-Parse-Application-Id")
    GCM_KEY = config.get("gcm", "API-Key")

if os.environ.get("SECRET_KEY"):
    SECRET_KEY = os.environ.get("SECRET_KEY")
else:
    with open('germany_app_engine/app.yaml') as f:
        SECRET_KEY = yaml.load(f)["env_variables"]["SECRET_KEY"]


def get_endpoint():
    if is_production():
        return get_production_endpoint()
    else:
        return "http://localhost:8080"


def get_production_endpoint():
    return "http://weightliftinggermany.appspot.com"


def is_production():
    return os.environ.get("ENV") == "PRODUCTION"


def valid_secret_key(request):
    return 'X-Secret-Key' in request.headers and request.headers["X-Secret-Key"] == SECRET_KEY


def send_get(path, endpoint=get_endpoint()):
    r = requests.get(endpoint + path, headers={"X-Secret-Key": SECRET_KEY})
    return r.content


def send_post(payload, path):
    r = requests.post(get_endpoint() + path, json=payload, headers={"X-Secret-Key": SECRET_KEY})
    return r.content


def write_news(news_text):
    with codecs.open(NEWS_FILE, 'a', encoding='utf8') as f:
        f.write(news_text)


def read_news():
    news = []
    if os.path.isfile(NEWS_FILE):
        with codecs.open(NEWS_FILE, 'r', encoding='utf8') as f:
            news = f.readlines()
        os.remove(NEWS_FILE)
    return news


def send_to_slack(text, username="Germany", important=True):
    color = "#ff0000" if important else "#ffffff"
    requests.post(SLACK_KEY, data=json.dumps({"username": username, "attachments": [{"color": color, "text": text}]}))


def notify_users_about_dev_news(title, message):
    notify_users(title, message, dev_news=True)


def notify_one_user(token, msg):
    gcm = GCM(GCM_KEY)
    data = {'update': msg.encode('utf-8')}
    gcm_push_response = gcm.json_request(registration_ids=[token], data=data)
    if bool(gcm_push_response):
        print token[:20] + " is invalid or outdated"
    else:
        print "Sent " + msg.encode('utf-8') + " to " + token[:20]


def notify_users_about_article(article):
    message = ""
    if len(article["content"]) > 30:
        message = article["content"][:30] + "..."
    else:
        message = article["content"]
    notify_users(article["heading"], message, article["publisher"], 2, 0)


def notify_users(title, message, description=None, fragmentId=None, subFragmentId=None, dev_news=False):
    '''New Article      #Victory in Berlin #Schwedt                  #2#0
       New Competition  #Schwedt vs. Berlin#1. Bundesliga - Staffel A#4#1
       Developer Heading#Developer Message                             '''
    if dev_news:
        msg = "#".join([title, message])
    else:
        msg = "#".join([title, message, description, str(fragmentId), str(subFragmentId)])
    gcm_token_objects = json.loads(send_get('/get_tokens'))['result']
    gcm = GCM(GCM_KEY)
    data = {'update': msg.encode('utf-8')}
    sent_requests = 0
    receivers = []
    for token in gcm_token_objects:
        if token not in receivers:
            gcm_push_response = gcm.json_request(registration_ids=[token], data=data)
            if bool(gcm_push_response):
                print token[:20] + " is invalid. Sending request to remove it."
                send_post({"token": token}, "/delete_token")
            else:
                print "Sent " + msg.encode('utf-8') + " to " + token[:20]
                receivers.append(token)
                sent_requests += 1
        else:
            print token[:20] + " is already saved. Sending request to remove it."
            send_post({"token": token}, "/delete_token")
    print "Sent to " + str(sent_requests) + " receivers"


def notify_users_about_developer_news(title, message):
    notify_users(title, message, "Willi Gierke (App Developer)", 0, 0)


def update_readme(blog_parsers_instances):
    headers = ["Blog Name", "Heading", "Date", "Image", "Content"]
    table = list()
    for blog_parser_instance in blog_parsers_instances:
        newest_url = blog_parser_instance.get_newest_article_url()
        page = urllib2.urlopen(newest_url).read()
        article = blog_parser_instance.parse_article_from_html(page)
        row = [blog_parser_instance.BLOG_NAME,
               u"[{}]({})".format(article["heading"], newest_url),
               datetime.fromtimestamp(float(article["date"])).strftime("%Y-%m-%d"),
               u"<img src='{}' width='100px'/>".format(article["image"]) if article["image"] else "",
               article["content"][:20] + "..."
               ]
        table.append(row)
    table = sorted(table, key=lambda k: datetime.strptime(k[2], "%Y-%m-%d"), reverse=True)

    with codecs.open("README.md", 'r', encoding='utf8') as f:
        readme = f.read()
    before_news = readme.split("## Current News")[0]
    new_readme = before_news + "## Current News\n\n" + tabulate(table, headers, tablefmt="pipe")
    with codecs.open("README.md", 'w', encoding='utf8') as f:
        f.write(new_readme)


def update_repo():
    commands = [["date", '+"%T"'],
                ["git", "fetch", "--all"],
                ["git", "reset", "--hard", "origin/master"]]
    for cmd in commands:
        subprocess.call(cmd)


def commit_changes():
    message = "".join(read_news())
    commands = [["git", "add", "--all"],
                ["git", "commit", "-m", u"{}".format(message)],
                ["git", "push"]]
    for cmd in commands:
        subprocess.call(cmd)


def print_buli_filters():
    filter_responses = send_get('/get_filters', endpoint=get_production_endpoint())
    filter_objects = json.loads(filter_responses)["result"]
    filters = [f["filterSetting"] for f in filter_objects]
    print "Collected " + str(len(filters)) + " buli filter settings:"
    filters = Counter(filters).most_common()
    filters.insert(0, ('Filter', 'Count'))
    print tabulate(filters)


def print_blog_filters():
    filter_responses = send_get('/get_blog_filters', endpoint=get_production_endpoint())
    filter_objects = json.loads(filter_responses)["result"]
    filters = [f["blogFilterSetting"] for f in filter_objects]
    print "Collected " + str(len(filters)) + " blog filter settings:"
    filters = Counter(filters).most_common()
    filters.insert(0, ('BlogFilter', 'Count'))
    print tabulate(filters)


def print_shared_protocols():
    filter_responses = send_get('/get_protocols', endpoint=get_production_endpoint())
    filter_objects = json.loads(filter_responses)["result"]
    filters = [f["parties"] for f in filter_objects]
    print "Collected " + str(len(filters)) + " shared protocols:"
    filters = Counter(filters).most_common()
    filters.insert(0, ('Share', 'Count'))
    print tabulate(filters)
