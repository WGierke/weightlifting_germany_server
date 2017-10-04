import json
import logging
import time
import urllib
from datetime import datetime

import webapp2
from google.appengine.api import memcache
from google.appengine.ext import ndb
from server_utils import json_serial, json_deserial, authenticated

DEFAULT_ARTICLE_VALUE = 'default_url'


def article_key(url=DEFAULT_ARTICLE_VALUE):
    return ndb.Key('Article', url)


def add_article_to_cache(url, article_dict):
    if not memcache.add('{}:article'.format(url), json.dumps(article_dict, default=json_serial), time=60 * 60 * 24 * 7):
        logging.error('Memcache set failed for article ' + article_dict["heading"])


class Article(ndb.Model):
    """A published article about German weightlifting"""
    url = ndb.StringProperty(indexed=True)
    publisher = ndb.StringProperty(indexed=True)
    heading = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now=False)
    image = ndb.StringProperty(indexed=False)


class GetArticles(webapp2.RequestHandler):
    @authenticated
    def get(self):
        publisher = self.request.get('publisher')
        offset = self.request.get('offset')
        offset = offset if offset != '' else 0
        articles = Article.query(Article.publisher == publisher).order(-Article.date)
        article_array = []
        for article_entity in articles.fetch(10, offset=offset):
            article_dict = {"url": article_entity.url}
            article_array.append(article_dict)
        response_dict = {"result": article_array}
        self.response.write(json.dumps(response_dict, encoding='latin1'))


class GetArticle(webapp2.RequestHandler):
    def load_article_from_store(self, url):
        article_query = Article.query(ancestor=article_key(url))
        articles = article_query.fetch(100)
        if len(articles) > 0:
            article = articles[0]
            add_article_to_cache(url, article.to_dict())
            return article

    @authenticated
    def get(self):
        url = urllib.unquote(self.request.query_string).decode('utf8').split("url=")[1]
        article_json = memcache.get('{}:article'.format(url))
        if article_json is None:
            article = self.load_article_from_store(url)
            if not article:
                self.response.write('No article found')
                return
        else:
            article = Article(**json.loads(article_json, object_pairs_hook=json_deserial))

        result = {"url": article.url, "date": str(time.mktime(article.date.timetuple())),
                  "heading": article.heading, "publisher": article.publisher,
                  "content": article.content, "image": article.image}
        response_dict = {"result": result}
        self.response.write(json.dumps(response_dict, encoding='utf-8'))


class AddArticle(webapp2.RequestHandler):
    def post(self):
        url = self.request.get("url")
        article_json = memcache.get('{}:article'.format(url))
        if article_json is not None:
            self.response.write('This article is already saved')
            return
        article_query = Article.query(ancestor=article_key(url))
        articles = article_query.fetch(100)
        if len(articles) == 0:
            article_entity = Article(parent=article_key(url))
            article_entity.url = url
            article_entity.publisher = self.request.get('publisher')
            article_entity.heading = self.request.get('heading')
            article_entity.content = self.request.get('content')
            article_entity.image = self.request.get('image')
            date = self.request.get('date')
            article_entity.date = datetime.fromtimestamp(float(date))
            article_entity.put()
            add_article_to_cache(url, article_entity.to_dict())
            self.response.write('Added article successfully')
        else:
            add_article_to_cache(url, articles[0].to_dict())
            self.response.write('This article is already saved')


class DeleteArticle(webapp2.RequestHandler):
    def post(self):
        url = self.request.get('url')
        article_query = Article.query(ancestor=article_key(url))
        articles = article_query.fetch(100)
        if len(articles) > 0:
            for article_entity in articles:
                article_entity.key.delete()
            self.response.write('Deleted article successfully')
        else:
            self.response.write('No article found')


class ArticleExists(webapp2.RequestHandler):
    def post(self):
        url = self.request.get("url")
        article_query = Article.query(ancestor=article_key(url))
        articles = article_query.fetch(100)
        if len(articles) > 0:
            self.response.write('Yes')
        else:
            self.response.write('No')
