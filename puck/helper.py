# -*- coding: utf-8 -*-
from .globals import current_app
import simplejson as json


def make_response(*args):
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

    return make_response(
        jsonify(
            data=data,
            code=code,
            message=message
        ), status_code
    )
