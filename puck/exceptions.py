# -*- coding: utf-8 -*-
from .response import Response
from .helper import api_response
from .constants import HTTP_CODES


class HTTPException(Exception):
    """A base Exception class"""

    def __init__(self, status_code, message=None, use_api_response=True):
        Exception.__init__(self, status_code, message)
        self.use_api_response = use_api_response
        self.status_code = status_code
        if message:
            self.message = message
        else:
            self.message = HTTP_CODES[self.status_code]

    def make_header(self):
        """Return a list of response header.
        Only used when ' self.use_api_response=False '
        """
        return [('Content-Type', 'text/html')]

    def make_response_body(self):
        """Generate a response body. It should be iterable.
        Only used when ' self.use_api_response=False '
        """
        return (
            '<title>%(status_code)d: %(status)s</title>\n'
            '<h1>Error! %(status_code)d: %(status)s</h1>'
            'Error Reason: %(message)s\n'
        ) % {
            'status_code': self.status_code,
            'status': HTTP_CODES[self.status_code],
            'message': self.message
        }

    def make_response(self):
        """Return a response object.
        Only used when ' self.use_api_response=False '
        """
        header = self.make_header()
        response_body = self.make_response_body()
        return Response(
            status=self.status_code, header=header,
            response_body=response_body
        )

    def __call__(self, environ, start_response):
        if self.use_api_response:
            response = api_response(
                status_code=self.status_code,
                code=self.status_code,
                message=self.message
            )
        else:
            response = self.make_response()
        return response(environ, start_response)


class BadRequest(HTTPException):
    """400: Bad Request

    Raise if the browser sends something to the application the application
    or server cannot handle.
    """
    def __init__(self, message=None, use_api_response=True):
        super(BadRequest, self).__init__(
            400, message=message, use_api_response=use_api_response
        )


class Unauthorized(HTTPException):
    """401: Unauthorized

    Raise if the user is not authorized.
    """
    def __init__(self, message=None, use_api_response=True):
        super(Unauthorized, self).__init__(
            401, message=message, use_api_response=use_api_response
        )


class Forbidden(HTTPException):
    """403: Forbidden

    Raise if the user doesn't have the permission for the requested resource
    but was authenticated.
    """
    def __init__(self, message=None, use_api_response=True):
        super(Forbidden, self).__init__(
            403, message=message, use_api_response=use_api_response
        )


class NotFound(HTTPException):
    """404: Not Found

    Raise if cannot find the resource.
    """
    def __init__(self, message=None, use_api_response=True):
        super(NotFound, self).__init__(
            404, message=message, use_api_response=use_api_response
        )


class MethodNotAllowed(HTTPException):
    """405: Method Not Allowed

    Raise if the server used a method the resource does not handle.  For
    example If a resource only accept 'POST' request, but a user send a
    'GET' request, this exception will be raised.
    """
    def __init__(self, message=None, use_api_response=True):
        super(MethodNotAllowed, self).__init__(
            405, message=message, use_api_response=use_api_response
        )


class InternalServerError(HTTPException):
    """500: Internal Server Error

    Raise if an internal server error occurred.
    """
    def __init__(self, message=None, use_api_response=True):
        super(InternalServerError, self).__init__(
            500, message=message, use_api_response=use_api_response
        )


class BadGateway(HTTPException):

    def __init__(self, message=None, use_api_response=True):
        super(BadGateway, self).__init__(
            502, message=message, use_api_response=use_api_response
        )
