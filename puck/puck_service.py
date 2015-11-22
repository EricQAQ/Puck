# -*- coding: utf-8 -*-
from server_adapter import WSGIrefServer


class PuckApplication(object):

    def __init__(self):
        pass

    def add_url(self):
        """Add a url to PuckApp"""
        pass

    def get_puck_wsgi_application(self):
        """get the handler func of Puck App"""
        def puck_application_handler(environ, start_response):
            pass
        return puck_application_handler

    def run(self, host='127.0.0.1', port=8020, **kwargs):
        """use this func to start service in development env"""
        app = self.get_puck_wsgi_application()
        server = WSGIrefServer(host, port, **kwargs)
        server.run(app)
