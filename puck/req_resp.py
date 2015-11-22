# -*- coding: utf-8 -*-


class BaseRequest(object):

    @property
    def methods(self):
        pass

    @property
    def headers(self):
        pass

    @property
    def cookies(self):
        pass


class BaseResponse(object):
    pass


class Request(BaseRequest):
    pass


class Response(BaseResponse):
    pass
