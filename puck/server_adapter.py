"""
In this file, mainly handle choosing which WSGI Server to start
the service.
"""

# -*- coding: utf-8 -*-
from SocketServer import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, make_server


class BaseServer(object):
    """Base Server class"""
    def __init__(self, host, port, **kwargs):
        self.host = host
        self.port = port
        self.kws = kwargs

    def run(self, app):
        """To start the TCP server.
        Child Class should override this function"""
        pass


class NewWSGIServer(ThreadingMixIn, WSGIServer):
    """Support multi-thread"""
    pass


class WSGIrefServer(BaseServer):
    """Use wsgiref to build a server"""
    def run(self, wsgi_handler):
        server = make_server(
            host=self.host,
            port=self.port,
            app=wsgi_handler,
            server_class=NewWSGIServer
        )
        server.serve_forever()
