# -*- coding: utf-8 -*-
from .request import Request
from .response import Response
from .routing import Router
from .constants import HTTP_CODES
from .session import RedisPickleSession
from .globals import request_stack, request

from .exceptions import HTTPException, NotFound, MethodNotAllowed
from .utils import local_time_2_utc, get_after_input_time


# the default secure key, if secure_key is not set, use this constant to set it.
DEFAULT_SECURE_KEY = 'Puck'


class Puck(object):

    request_class = Request
    response_class = Response

    def __init__(self, redis_host='127.0.0.1', redis_port=6379,
                 session_key='session_id', secure_key=None):

        # the secure_key, which will be used to sign.
        self.secure_key = secure_key if secure_key else DEFAULT_SECURE_KEY

        # the name of session_id, default value is 'session_id'
        self.session_key = session_key

        # the type of sessions' storage, currently Puck support to use Redis to
        # save the session.
        self.session_type = RedisPickleSession(
            redis_host=redis_host, redis_port=redis_port,
            secure_key=self.secure_key, key=session_key
        )

        self.url_handler_map = Router()

        # a list of functions that will be called before handling
        # the request. If these functions return any value, the
        # further request handling is stopped, and instance of Puck
        # will use this value to make response.
        self.before_request_funcs = []

        # a list of functions that will be called at the end of the
        # request. The response object should be passed to these
        # functions, and thes functions may change the response
        # object.
        self.after_request_funcs = []

    def route(self, url, **options):
        """Decorator for request handler. Add rules.
        Same as add_route(url, handler, **optioins)
        Example:

            @app.route('/')
            def index():
                return 'Hello world'
        """
        def wrapper(handler):
            self.add_route(url, handler, **options)
            return handler
        return wrapper

    def add_route(self, url, handler, **options):
        """Add new rule to url_handler_map"""
        options.setdefault('methods', ('GET',))
        options.setdefault('rule_name', handler.__name__)
        self.url_handler_map.add(url, handler, **options)

    def before_request(self, func):
        """Registers a function to run before handling every request."""
        self.before_request_funcs.append(func)
        return func

    def after_request(self, func):
        """Registers a function to run after handling every request."""
        self.after_request_funcs.append(func)
        return func

    def match_url(self, url, method):
        """According the request url, to matching the handler.
        If cannot find a handler, return (None, None, None)

        :return: (function, methods, params)"""
        return self.url_handler_map.match_url(url, method)

    def process_before_request(self):
        """Called the functions before dispatching the request url, which
        uses "@before_request" to decorate function. All these functions
        are stored in a list named "before_request_funcs".
        If any of these function returns a value, the further request
        handling is stopped, in other words, If any of these function can
        return a value, Puck will use this value to make response.
        """
        for func in self.before_request_funcs:
            result = func()
            if result is not None:
                return result

    def process_after_request(self, response):
        """This function will be called after handling the request
        and make the response.All these functions
        are stored in a list named "after_request_funcs.
        If the session is not None, the session will be saved.

        :param response: the ojbect of response. Always the return
                         value of make_respose
        """
        _session = request_stack.top.session
        if _session is not None:
            self.save_session(_session, response)
        for func in self.after_request_funcs:
            response = func(response)
        return response

    def get_session(self, request):
        """Get the current session in current request.
        If the session is not exist, it will create a new session.

        :param request: an instance of request_class.
        """
        if self.secure_key:
            return self.session_type.load_session(request, self.session_key)

    def save_session(self, session, response, expire=None, path=None,
                     domain=None, secure=None, httponly=False):
        """Saves the session if it needs updates.

        :param session: the session will be saved
        :param response: the response object, the instance of response_class
        :param expire: the expire time, an instance of datetime
        """
        if expire:
            real_expire_time = get_after_input_time(expire)
            expire = local_time_2_utc(real_expire_time)
        if session is not None:
            self.session_type.save_session(session, response, expire, path,
                                           domain, secure, httponly)

    def make_response(self, response):
        """
        Make response.

        1. if the param response is a tuple, this func will create an instance of Response
        2. Set the status of the instance of Response.
        """
        status = header = None

        if isinstance(response, tuple):
            response, status, header = response + (None,) * (3 - len(response))

        if not isinstance(response, self.response_class):
            if isinstance(response, basestring):
                response = self.response_class(
                    response_body=response.encode('utf-8'), header=header)
            else:
                response = self.response_class(response_body=response, header=header)

        if status is not None:
            if isinstance(status, basestring):
                response.status = status
            else:
                response.status = '%d %s' % (status, HTTP_CODES[status])

        return response

    # def handle(self, handler, methods, request_method, params):
    #     if handler is None:
    #         self.notfound()
    #     if request_method not in methods:
    #         self.abort(405)
    #     return handler(**params)

    # def notfound(self):
    #     raise NotFound()
    #
    # def abort(self, status_code):
    #     raise MethodNotAllowed()

    def __call__(self, environ, start_response):
        """WSGI interface. The server will call the instance of Puck, use
        this function to handling request. """
        with _RequestStack(self, environ):
            result = self.process_before_request()
            if result is None:
                request_url = request.path
                request_method = request.method

                try:
                    handler, params = self.match_url(request_url, request_method)
                    result = handler(**params)
                    # result = self.handle(handler, methods, request_method, params)
                except HTTPException as ex_response:
                    return ex_response(environ, start_response)

            response = self.make_response(result)
            response = self.process_after_request(response)
            return response(environ, start_response)

    def run(self, host='127.0.0.1', port=8888, **options):
        # options.setdefault('use_server', 'WSGIrefServer')
        from server import WSGIrefServer
        httpd = WSGIrefServer(host=host, port=port, **options)
        httpd.run(self)


class _RequestStack(object):
    """
    The stack of the request. When the request comes to Puck, use this class like this:

        with _RequestStack(Puck, environ):
            xxx
            xxx
    Use this context, it will push the current app, the current request and the session
    into the LocalStack
    """
    def __init__(self, app, environ):
        self.app = app
        self.request = app.request_class(environ)
        self.session = app.get_session(self.request)

    def __enter__(self):
        request_stack.push(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            request_stack.pop()
