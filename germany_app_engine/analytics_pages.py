import json
import webapp2
from google.appengine.ext import ndb
from server_utils import valid_secret_key

DEFAULT_PARTIES_VALUES = 'default_parties'
DEFAULT_USER_ID = 'default_user'
DEFAULT_FILTER_VALUE = 'default_filter'


def filter_key(user_id=DEFAULT_USER_ID):
    return ndb.Key('Filter', user_id)


def blog_filter_key(user_id=DEFAULT_USER_ID):
    return ndb.Key('BlogFilter', user_id)


def protocol_key(parties=DEFAULT_PARTIES_VALUES):
    return ndb.Key('SharedProtocol', parties)


class FilterSetting(ndb.Model):
    """Club/Relay a user uses as filter"""
    user_id = ndb.StringProperty(indexed=False)
    filter_setting = ndb.StringProperty(indexed=False)
    timestamp = ndb.DateTimeProperty(auto_now=True)


class BlogFilterSetting(ndb.Model):
    """Blog a user uses as filter"""
    user_id = ndb.StringProperty(indexed=False)
    filter_setting = ndb.StringProperty(indexed=False)
    timestamp = ndb.DateTimeProperty(auto_now=True)


class SharedProtocol(ndb.Model):
    """Protocol that was shared"""
    competition_parties = ndb.StringProperty(indexed=False)
    timestamp = ndb.DateTimeProperty(auto_now=True)


class GetFilters(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            filter_query = FilterSetting.query()
            filters = filter_query.fetch(1000)
            filter_array = []
            for filter_entity in filters:
                filter_dict = {"userId": filter_entity.user_id, "createdAt": filter_entity.timestamp.strftime("%s"),
                               "filterSetting": filter_entity.filter_setting}
                filter_array.append(filter_dict)
            response_dict = {"result": filter_array}
            self.response.write(json.dumps(response_dict, encoding='latin1'))
        else:
            self.response.out.write('Secret Key is not valid')


class AddFilter(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            user_id = self.request.get('userId')
            filter_setting = self.request.get('filterSetting')
            filter_query = FilterSetting.query(ancestor=filter_key(user_id))
            filters = filter_query.fetch(100)
            if len(filters) == 0:
                filter_entity = FilterSetting(parent=filter_key(user_id))
                filter_entity.filter_setting = filter_setting
                filter_entity.user_id = user_id
                filter_entity.put()
                self.response.write('Added filter successfully')
            else:
                for filter_entity in filters:
                    filter_entity.filter_setting = filter_setting
                    filter_entity.user_id = user_id
                    filter_entity.put()
                    self.response.write('Filter was updated successfully')
        else:
            self.response.out.write('Secret Key is not valid')


class DeleteFilter(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            user_id = self.request.get('userId')
            filter_query = FilterSetting.query(ancestor=filter_key(user_id))
            filter_settings = filter_query.fetch(100)
            if len(filter_settings) > 0:
                for filter_entity in filter_settings:
                    filter_entity.key.delete()
                self.response.write('Deleted filter successfully')
            else:
                self.response.write('No filter found')
        else:
            self.response.out.write('Secret Key is not valid')


class GetBlogFilters(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            blog_filter_query = BlogFilterSetting.query()
            blog_filters = blog_filter_query.fetch(1000)
            filter_array = []
            for blog_filter_entity in blog_filters:
                filter_dict = {"userId": blog_filter_entity.user_id, "createdAt": blog_filter_entity.timestamp.strftime("%s"),
                               "blogFilterSetting": blog_filter_entity.filter_setting}
                filter_array.append(filter_dict)
            response_dict = {"result": filter_array}
            self.response.write(json.dumps(response_dict, encoding='latin1'))
        else:
            self.response.out.write('Secret Key is not valid')


class AddBlogFilter(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            user_id = self.request.get('userId')
            filter_setting = self.request.get('blogFilterSetting')
            blog_filter_query = BlogFilterSetting.query(ancestor=blog_filter_key(user_id))
            blog_filters = blog_filter_query.fetch(100)
            if len(blog_filters) == 0:
                blog_filter_entity = BlogFilterSetting(parent=blog_filter_key(user_id))
                blog_filter_entity.filter_setting = filter_setting
                blog_filter_entity.user_id = user_id
                blog_filter_entity.put()
                self.response.write('Added blog filter successfully')
            else:
                for blog_filter_entity in blog_filters:
                    blog_filter_entity.filter_setting = filter_setting
                    blog_filter_entity.user_id = user_id
                    blog_filter_entity.put()
                    self.response.write('Blog filter was updated successfully')
        else:
            self.response.out.write('Secret Key is not valid')


class DeleteBlogFilter(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            user_id = self.request.get('userId')
            blog_filter_query = BlogFilterSetting.query(ancestor=blog_filter_key(user_id))
            filter_settings = blog_filter_query.fetch(100)
            if len(filter_settings) > 0:
                for blog_filter_entity in filter_settings:
                    blog_filter_entity.key.delete()
                self.response.write('Deleted blog filter successfully')
            else:
                self.response.write('No blog filter found')
        else:
            self.response.out.write('Secret Key is not valid')


class GetSharedProtocols(webapp2.RequestHandler):
    def get(self):
        if valid_secret_key(self.request):
            protocol_query = SharedProtocol.query()
            shared_protocols = protocol_query.fetch(1000)
            protocol_array = []
            for protocol_entity in shared_protocols:
                protocol_dict = {"parties": protocol_entity.competition_parties,
                                 "createdAt": protocol_entity.timestamp.strftime("%s")}
                protocol_array.append(protocol_dict)
            response_dict = {"result": protocol_array}
            self.response.write(json.dumps(response_dict, encoding='latin1'))
        else:
            self.response.out.write('Secret Key is not valid')


class AddSharedProtocol(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            competition_parties = self.request.get('competitionParties')
            protocol_query = SharedProtocol.query(ancestor=protocol_key(competition_parties))
            protocols = protocol_query.fetch(100)
            if len(protocols) == 0:
                protocol_entity = SharedProtocol(parent=protocol_key(competition_parties))
                protocol_entity.competition_parties = competition_parties
                protocol_entity.put()
                self.response.write('Added protocol successfully')
            else:
                self.response.write('This protocol is already saved')
        else:
            self.response.out.write('Secret Key is not valid')


class DeleteSharedProtocol(webapp2.RequestHandler):
    def post(self):
        if valid_secret_key(self.request):
            competition_parties = self.request.get('competitionParties')
            protocol_query = SharedProtocol.query(ancestor=protocol_key(competition_parties))
            protocols = protocol_query.fetch(100)
            if len(protocols) > 0:
                for protocol_entity in protocols:
                    protocol_entity.key.delete()
                self.response.write('Deleted protocol successfully')
            else:
                self.response.write('No protocol found')
        else:
            self.response.out.write('Secret Key is not valid')
