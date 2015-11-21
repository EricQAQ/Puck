# -*- coding: utf-8 -*-
from wsgiref.simple_server import make_server

__author__ = 'Eric Zhang'


class BaseServer(object):
    """Base Server class"""
    def __init__(self, host, port, **kwargs):
        self.host = host
        self.port = port
        self.kws = kwargs

    def run(self, app):
        """To start the server.
        Child Class should override this function"""
        pass


class WSGIServer(BaseServer):
    """Use wsgiref to build a server"""
    def run(self, app):
        server = make_server(host=self.host, port=self.port, app=app)
        server.serve_forever()
