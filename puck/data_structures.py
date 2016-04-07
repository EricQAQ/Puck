# -*— coding:utf-8 -*-
from warnings import warn


class Header(object):
    """Store response header.
    Header class support two ways to initialize:
    1. Supply a dict object, get_content_type
    2. DO NOT Supply a dict object, but gives key-value pairs, get_content_type
    """
    def __init__(self, _dict=None, *args, **kwargs):
        self._dict = dict()
        if not _dict:
            for key, value in dict(*args, **kwargs).iteritems():
                self._dict[key] = value

        elif not isinstance(_dict, dict):
            warn(
                'The response head is initialized to None, '
                'because the param is not dict.', UserWarning
            )
        else:
            for key, value in _dict.iteritems():
                self._dict[key] = value

    def __setitem__(self, key, value):
        key = self.http_key(key)
        value = str(value)
        self._dict[key] = value

    def __getitem__(self, item):
        item = self.http_key(item)
        return self._dict[item]

    def __delitem__(self, key):
        key = self.http_key(key)
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def http_key(self, key):
        """content-type --> Content-Type"""
        return key.replace('_', '-').title()


class RequestHeader(Header):

    def __init__(self, environ):
        self.environ = environ

    def __len__(self):
        return len(dict(iter(self)))

    def __getitem__(self, item):
        item = self.handle_http_key(item)
        if item in ('CONTENT_LENGTH', 'CONTENT_TYPE'):
            return self.environ[item]
        return self.environ['HTTP_' + item]

    def __iter__(self):
        for key, value in self.environ.iteritems():
            if key.startswith('HTTP_') and \
                            key not in ('HTTP_CONTENT_LENGTH', 'HTTP_CONTENT_TYPE'):
                yield self.http_key(key[5:]), value
            elif key in ('CONTENT_LENGTH', 'CONTENT_TYPE'):
                yield self.http_key(key), value

    def handle_http_key(self, key):
        """content-type --> CONTENT_TYPE"""
        return key.upper().replace('-', '_')
