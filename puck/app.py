from local import LocalStack
from request import Request
from response import Response
from routing import Router
from .exceptions import HTTPException


class Puck(object):

    request_class = Request
    response_class = Response

    def __init__(self):

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
        pass

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

    def match_url(self, url):
        """According the request url, to matching the handler.
        If cannot find a handler, return (None, None, None)

        :return: (function, methods, params)"""
        return self.url_handler_map.match_url(url)

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
        for func in self.after_request_funcs:
            response = func(response)
        return response

    def make_response(self, response):
        status = header = None

        if isinstance(response, tuple):
            response, status, header = response + (None,) * (3 - len(response))

        if not isinstance(response, self.response_class):
            if status is None:
                response = self.response_class(response_body=response, header=header)
            else:
                response = self.response_class(response_body=response, header=header, status=status)

        if isinstance(response, basestring):
            response = self.response_class(response_body=response.encode('utf-8'))

        return response

    def handle(self, handler, methods, request_method, params):
        if not handler:
            self.notfound()
        if request_method not in methods:
            self.abort(405)
        return handler(**params)

    def notfound(self):
        pass

    def abort(self, status_code):
        pass

    def __call__(self, environ, start_response):
        """WSGI interface. The server will call the instance of Puck, use
        this function to handling request. """
        with _RequestStack(self, environ) as current_request:
            result = self.process_before_request()
            if result is None:
                request_url = current_request.request.path
                request_method = current_request.request.methods
                try:
                    handler, methods, params = self.match_url(request_url)
                    result = self.handle(handler, methods, request_method, params)
                except HTTPException as e:
                    pass

            response = self.make_response(result)
            response = self.process_after_request(response)
            return response(environ, start_response)

    def run(self, host='127.0.0.1', port='8888', **options):
        # options.setdefault('use_server', 'WSGIrefServer')
        from server import WSGIrefServer
        httpd = WSGIrefServer(host=host, port=port, **options)
        httpd.run(self)


class _RequestStack(object):

    def __init__(self, app, environ):
        self.app = app
        self.request = app.request_class(environ)

    def __enter__(self):
        request_stack.push(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            request_stack.pop()


request_stack = LocalStack()
request = request_stack.top.request if request_stack.top else None
current_app = request_stack.top.app if request_stack.top else None
