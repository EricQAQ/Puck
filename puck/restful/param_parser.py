# -*- coding: utf-8 -*-
from puck.globals import request


class Param(object):

    def __init__(self, name, d_type=str, append=False, required=False,
                 spell_sensitive=False):
        # the name of the param
        self.name = name

        # the data type of the param
        self.d_type = d_type

        self.append = append

        # the flag whether this param is necessary
        self.required = required

        # whether the name of param is sensitive
        self.sensitive = spell_sensitive

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__, str(self.__class__.__dict__)
        )
        # return 'class: Param, name: {}, type: {}, append: {},' \
        #        ' required: {}, sensitive: {}'.format(
        #     self.name, str(self.d_type), str(self.append),
        #     str(self.required), str(self.sensitive)
        # )

    def __str__(self):
        self.__repr__()


class BaseRequestParamParser(object):

    def __init__(self):

        # a list of params, each one is an instance of Param
        self.params = []

    def get(self, name):
        """Return the instance of Param from params if the name is match."""
        for item in self.params:
            item_name = item.name
            if not item.sensitive:
                item_name = item_name.lower()
            if item_name == name:
                return item
        return None

    def add_param(self, param):
        """Add new param"""
        if isinstance(param, Param):
            self.params.append(param)

    def parse_request_param(self):
        """Parse the params that gives from the request"""
        _dict = {}

        method = request.method
        param_dict = request.request_params
        if method in ('POST', 'PUT'):
            for key, value in request.form:
                param_dict[key] = value

        # compares the params of the request and the pre-defined params.
        # NOTE the Param.required, if it is True, that means this param is necessary.
        for item in self.params:
            if item.required and item.name not in param_dict:
                raise ValueError(
                    'The key: {key} is not exist in this request.'.format(key=item.name))
            if item.name in param_dict:
                try:
                    _dict[item.name] = item.d_type(param_dict[item.name])
                except TypeError:
                    raise TypeError(
                        'The value of {key} cannot convert into {type}'.
                            format(key=item.name, type=item.d_type.__name__)
                    )
        return _dict


class RequestParamParser(BaseRequestParamParser):

    def __init__(self):
        super(RequestParamParser, self).__init__()
        self._auto_add_parser_param()

    def _auto_add_parser_param(self):
        """Auto add the params which the user gives in the
        child class for RequestParamParser
        """
        for value in self.__class__.__dict__.values():
            if isinstance(value, Param):
                self.add_param(value)
