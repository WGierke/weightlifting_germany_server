import requests
import json
import os
import ConfigParser
import codecs
import urllib2
import subprocess
from datetime import datetime
from tabulate import tabulate

NEWS_FILE = "news.txt"

if os.path.isfile("config.ini"):
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('config.ini')
    SLACK_KEY = config.get("slack", "Webhook")

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

def notify_users(article):
    # Notify app users
    send_to_slack("New article: " + article["heading"], username=article["publisher"], important=False)

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
               "<img src='{}' width='100px'/>".format(article["image"]) if article["image"] else "",
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
