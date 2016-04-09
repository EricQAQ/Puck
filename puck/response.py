import warnings
from Cookie import SimpleCookie

from data_structures import Header
from utils import generate_content_type
from cookies import generate_cookie


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
                self.status_code = int(status)
            except TypeError:
                self.status_code = self.default_status
                warnings.warn(
                    'Status code is initialized to 200, Because the '
                    'status code should be int.',
                    UserWarning
                )

        # Get the response body
        if response_body is None:
            self.response = {}
        else:
            self.response = response_body

    @property
    def cookies(self):
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


class Response(BaseResponse):
    pass
