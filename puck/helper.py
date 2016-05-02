# -*- coding: utf-8 -*-
from .globals import current_app
import simplejson as json


def make_response(*args):
    """
    The helper function to make a response. It will call the make_response of the Puck(APP)
    """
    if not args:
        return current_app.response_class()

    return current_app.make_response(args)


def dumps(obj, **kwargs):
    kwargs.setdefault('ensure_ascii', False)
    js = json.dumps(obj, **kwargs)
    if isinstance(js, unicode):
        js.encode('utf-8')
    return js


def jsonify(*args, **kwargs):
    """ Create a instance of Response,
    and setting the mimetype='application/json' """
    return current_app.response_class(
        response_body=dumps(dict(*args, **kwargs)),
        mimetype='application/json'
    )


def api_response(data=None, status_code=200, code=200, message=None):
    """Response a json object. Always use this func when the users want to build web API.

    :param data: the data of the response, which will be transferred to JSON object
    :param status_code: the status code of the response.
    :param code: the API code, always used to handling the API exception(NOT the HTTP exception).
    :param message: the message of the API response object.
    """
    return make_response(
        jsonify(
            data=data,
            code=code,
            message=message
        ), status_code
    )
