# -*- coding: utf-8 -*-
"""
In this file, mainly handle choosing which WSGI Server to start
the service.
"""


class BaseServer(object):
    """Base Server class"""
    def __init__(self, host, port, **options):
        self.host = host
        self.port = port
        self.options = options

    def run(self, app):
        """To start the TCP server.
        Child Class should override this function"""
        pass


class WSGIrefServer(BaseServer):
    """Use wsgiref to build a server"""
    def run(self, app):
        from wsgiref.simple_server import make_server

        server = make_server(
            host=self.host,
            port=self.port,
            app=app,
            **self.options
        )
        server.serve_forever()
