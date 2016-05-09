# -*- coding: utf-8 -*-
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from .data_structures import EnvironHeader
from .cookies import parse_cookie
from .form import parse_form_data
from .utils import lazy_property


def get_host(environ):
    """Get real host
    If there is HTTP_X_FORWARDED_HOST in environ, use the value of it.
    """
    if 'HTTP_X_FORWARDED_HOST' in environ:
        return environ['HTTP_X_FORWARDED_HOST']
    elif 'HTTP_HOST' in environ:
        return environ['HTTP_HOST']

    request_host = environ['SERVER_NAME']
    if (environ['wsgi.url_scheme'], environ['SERVER_PORT']) not in \
            (('https', '443'), ('http', '80')):
        request_host += ':' + environ['SERVER_PORT']

    return request_host


class BaseRequest(object):

    def __init__(self, environ):
        self.environ = environ

    @lazy_property
    def method(self):
        return self.environ.get('REQUEST_METHOD', 'get').upper()

    @lazy_property
    def header(self):
        return EnvironHeader(self.environ)

    @lazy_property
    def cookies(self):
        """return the cookie.
        The cookie is a dict, user can get the key and value in dict way.
        The key is the cookie name, the value is the cookie value, not the instance of Morsel

        The cookies should be like this:

        {'session_id': '1', 'test': 'xxx'}
        """
        return parse_cookie(self.environ)

    @lazy_property
    def request_addr(self):
        """Get request address"""
        # TODO: Add support get real request address when use proxy(HTTP_X_FORWARDED_FOR)
        return self.environ['REMOTE_ADDR']

    @lazy_property
    def host(self):
        """Get real host address."""
        return get_host(self.environ)

    @lazy_property
    def path(self):
        path = '/' + self.environ.get('PATH_INFO', '').lstrip('/')
        # TODO 需要改变编码方式
        return path

    @lazy_property
    def content_type(self):
        return self.environ.get('CONTENT_TYPE', '')

    @lazy_property
    def request_params(self):
        """return the request params. Example:
        1. user try to visit http://example.com/?key=value&a=b, method is GET:
        It will get:
        param = {'key': 'value', 'a':'b'}

        2. user try to visit http://example.com/?key=value&a=b&a=c, method is GET:
        It will get:
        param = {'key': 'value', 'a':['b', 'c']}
        """
        raw_data = parse_qs(
            self.environ.get('QUERY_STRING', ''), keep_blank_values=True
        )
        params = {}
        for key, value in raw_data.iteritems():
            if len(value) == 1:
                params[key] = value[0]
            else:
                params[key] = value
        return params

    @lazy_property
    def form(self):
        if self.method not in ('POST', 'PUT'):
            return {}

        d = self.__dict__
        if '_form' not in d:
            d['_form'], d['_file'] = parse_form_data(self.environ)
        return self._form

    @lazy_property
    def file(self):
        if self.method not in ('POST', 'PUT'):
            return {}

        d = self.__dict__
        if '_file' not in d:
            d['_form'], d['_file'] = parse_form_data(self.environ)
        return self._file


class Request(BaseRequest):
    pass
