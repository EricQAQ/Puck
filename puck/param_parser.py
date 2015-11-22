# -*- coding: utf-8 -*-


def to_unicode(string):
    return unicode(string)


class Param(object):

    def __init__(self, name, type=to_unicode, append=False, required=False,
                 spell_sensitive=False):
        self.name = name
        self.type = type
        self.append = append
        self.required = required
        self.sensitive = spell_sensitive

    def __repr__(self):
        return 'class: Param, name: {}, type: {}, append: {},' \
               ' required: {}, sensitive: {}'.format(
            self.name, str(self.type), str(self.append),
            str(self.required), str(self.sensitive)
        )

    def __str__(self):
        self.__repr__()


class BaseRequestParamParser(object):

    def __init__(self):
        self.params = []

    def add_param(self, *args, **kwargs):
        """Add new param"""
        self.params.append(Param(*args, **kwargs))

    def parse_request_param(self, request):
        """Parse the params that gives from the request"""
        pass


class RequestParamParser(BaseRequestParamParser):

    def __init__(self):
        super(RequestParamParser, self).__init__()
        self._auto_add_parser_param()

    def _auto_add_parser_param(self):
        """Auto add the params which the user gives in the
        child class for RequestParamParser
        """
        for value in self.__class__.__dict__.items():
            self.add_param(value[0], value[1])
