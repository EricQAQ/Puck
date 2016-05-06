# -*- coding: utf-8 -*-
import warnings
from Cookie import SimpleCookie

from .data_structures import Header
from .utils import generate_content_type
from .cookies import generate_cookie
from .constants import HTTP_CODES


class BaseResponse(object):

    # the charset of response
    charset = 'utf-8'

    # the default mimetype if there is not given
    default_mimetype = 'text/html'

    # the default status code if there is not given
    default_status = 200

    def __init__(self, status=default_status, response_body=None, header=None,
                 mimetype=None, content_type=None):
        if isinstance(header, Header):
            self.header = header
        elif not header:
            self.header = Header()
        else:
            self.header = Header(header)

        # Set cookies.
        # cookies have two copies:
        # one is in response object(Type=SimpleCookie): self.cookies = [SimpleCookie_1, SimpleCookie_2]
        # another is in response header object(Type=str): header['Cookies']=['cookie_1', 'cookie_2']
        self._cookies = None
        # self.header['Cookies'] = []

        # Get the Content-Type
        if content_type is None:
            if mimetype is None and 'Content-Type' not in self.header:
                mimetype = self.default_mimetype
            if mimetype is not None:
                mimetype = generate_content_type(mimetype, self.charset)
            content_type = mimetype
        if content_type is not None:
            self.header['Content-Type'] = content_type

        # Get the status code OR status
        if isinstance(status, basestring):
            # Ex: status = '200 OK'
            self.status = status
        else:
            # Ex: status = 200
            try:
                # self.status_code = int(status)
                self.status = '%d %s' % (int(status), HTTP_CODES[int(status)])
            except TypeError:
                # self.status_code = self.default_status
                self.status = '%d %s' % (
                    self.default_status, HTTP_CODES[self.default_status])
                warnings.warn(
                    'Status code is initialized to 200, Because the '
                    'status code should be int.',
                    UserWarning
                )

        # Get the response body
        if response_body is None:
            self.response = []
        else:
            self.response = response_body

    @property
    def is_sequence(self):
        return isinstance(self.response, (list, tuple))

    @property
    def cookies(self):
        """self._cookies is a dict, key: cookie name, value: a instance of Morsel."""
        if not self._cookies:
            self._create_cookie()
        return self._cookies

    def _create_cookie(self):
        _dict = self.__dict__
        _dict['_cookies'] = SimpleCookie()

    def set_cookies(self, key, value='', expires=None, path=None, domain=None,
                    max_age=None, secure=None, httponly=False):
        """Set a cookie. The params are the same as the Morsel in Cookie which is a
        python standard library.

        :param key: the name of the cookie to be set
        :param value: the value of the cookie
        :param expires: should be a `datetime` object or UNIX timestamp.
        :param path: limit the cookie to the given path.
        :param domain: set a cross-domain cookie. Example:
                       domain=".example.com", it will set the cookie that is
                       readable by the domain "www.example.com"
        :param max_age: should be a number of seconds or None.
        :param secure: The cookie will only be available via HTTPS
        """
        morsel = generate_cookie(
            key, value, expires=expires, path=path, domain=domain,
            max_age=max_age, secure=secure, httponly=httponly
        )
        self.cookies[key] = morsel
        # self._create_cookies(morsel)
        # self.header['Cookies'].append(morsel)   # Update cookies to header.

    def delete_cookies(self, key, path, domain):
        """Delete the cookie from response.

        :param key: the name of the cookie to be delete
        :param path: limit the cookie to the given path. If the cookie was
                     limited to a path, user can use this param.
        :param domain: limit the cookie to the given domain. If the cookie was
                     limited to the domain, user can use this param.
        """
        self.set_cookies(key, path=path, domain=domain, max_age=0)

    # def _create_cookies(self, mosel):
    #     """Create a cookies attribute for response."""
    #     return self.cookies.append(SimpleCookie(mosel.output()))

    def get_header_list(self):
        """Turn the response header into a list. The header is a instance of Header,
        use this func to get attribute which name is ' _list '.
        """
        for item in self.cookies:
            self.header.add('Set-Cookie', self.cookies[item].OutputString())
        if self.is_sequence and 'Content-Length' not in self.header:
            try:
                content_length = sum((len(str(item))) for item in self.response)
            except UnicodeError:
                pass
            else:
                self.header.add('Content-Length', str(content_length))
        return self.header.head_to_list(charset=self.charset)

    def iterable_item(self, environ):
        """ Generate a iterable object, and use this object to return.

        :param environ: the WSGI environment
        :return: a iterable response
        """
        status_code = int(self.status[:3])
        if environ['REQUEST_METHOD'] == 'HEAD' or \
                    100 <= status_code < 200 or status_code in (204, 304):
            yield ()

        for item in self.response:
            if isinstance(item, unicode):
                yield item.encode(self.charset)
            else:
                yield str(item)

    def wsgi_response(self, environ):
        """Return the WSGI response as a tuple.

        :param environ: the WSGI environment
        :return: (obj_iter, status, header_list)
                 the first one is a iterable object, the second one is a string showing
                 the response status, like '200 OK', the last one is the list of the
                 response header.
        """
        obj_iter = self.iterable_item(environ)
        return obj_iter, self.status, self.get_header_list()

    def __call__(self, environ, start_response):
        """Make instance of Response class as a WSGI application.

        :param environ: the WSGI environment
        :param start_response: the response callable provided by the WSGI
                               server.
        :return: an iterable object.
        """
        obj_iter, status, headers = self.wsgi_response(environ)
        start_response(status, headers)

        return obj_iter


class Response(BaseResponse):
    pass
