import json
import time
import webapp2
from google.appengine.ext import ndb
from datetime import datetime
from utils import valid_secret_key

DEFAULT_ARTICLE_VALUE = 'default_url'


def article_key(url=DEFAULT_ARTICLE_VALUE):
    return ndb.Key('Article', url)


class Article(ndb.Model):
    """A published article about German weightlifting"""
    url = ndb.StringProperty(indexed=True)
    publisher = ndb.StringProperty(indexed=True)
    heading = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now=False)
    image = ndb.StringProperty(indexed=False)


class GetArticles(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            article_query = Article.query()
            articles = article_query.fetch(1000)
            article_array = []
            for article_entity in articles:
                article_dict = {"url": article_entity.url}
                article_array.append(article_dict)
            response_dict = {"result": article_array}
            self.response.write(json.dumps(response_dict, encoding='latin1'))
        else:
            self.response.out.write('Secret Key is not valid')


class GetArticle(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            url = self.request.get("url")
            article_query = Article.query(ancestor=article_key(url))
            articles = article_query.fetch(100)
            if len(articles) > 0:
                article = articles[0]
                result = {"url": article.url, "date": str(time.mktime(article.date.timetuple())), 
                          "heading": article.heading, "publisher": article.publisher,
                          "content": article.content, "image": article.image}
                response_dict = {"result": result}
                self.response.write(json.dumps(response_dict, encoding='utf-8'))
            else:
                self.response.write('No article found')
        else:
            self.response.out.write('Secret Key is not valid')


class AddArticle(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            url = self.request.get("url")
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
                self.response.write('Added article successfully')
            else:
                self.response.write('This article is already saved')
        else:
            self.response.out.write('Secret Key is not valid')


class DeleteArticle(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            url = self.request.get('url')
            article_query = Article.query(ancestor=article_key(url))
            articles = article_query.fetch(100)
            if len(articles) > 0:
                for article_entity in articles:
                    article_entity.key.delete()
                self.response.write('Deleted article successfully')
            else:
                self.response.write('No article found')
        else:
            self.response.out.write('Secret Key is not valid')


class ArticleExists(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            url = self.request.get("url")
            article_query = Article.query(ancestor=article_key(url))
            articles = article_query.fetch(100)
            if len(articles) > 0:
                self.response.write('Yes')
            else:
                self.response.write('No')
        else:
            self.response.out.write('Secret Key is not valid')
