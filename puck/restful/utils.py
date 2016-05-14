# -*- coding: utf-8 -*-
from functools import wraps

from ..helper import api_response


def variable_parser(parser_class):
    """Parse the variables according to parser_class.
    1. filter out the variables that the parser_class do not have
    2. Judge whether the necessary variables in the request or not

    :param parser_class: the parser class always a subclass of RequestParamParser
    """

    def raise_parser_error():
        return api_response(status_code=400)

    def decorate(func):
        @wraps(func)
        def wrappers(*args, **kwargs):
            try:
                variable_data = parser_class().parse_request_param()
            except (ValueError, TypeError) as error:
                return raise_parser_error()
            if args:
                args[0].variable_data = variable_data
                return func(*args, **kwargs)
            else:
                return func(variable_data=variable_data, **kwargs)

        return wrappers

    return decorate

