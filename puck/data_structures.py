# -*— coding:utf-8 -*-
from warnings import warn


def http_key(key):
    """content-type --> Content-Type"""
    return key.replace('_', '-').title()


class Header(object):
    """Store response header.
    Header class support three ways to initialize:
    1. Supply a dict object
    2. DO NOT Supply a dict or list object, but gives key-value pairs
    3. Supply a list object

    Data-structure:
    self._list = [(key1, value1), (key2, value2), ...]
    """
    def __init__(self, _dict_list=None, *args, **kwargs):
        # self._list = [(key, value), (key, value), ...]
        self._list = []
        if not _dict_list:
            for key, value in dict(*args, **kwargs).iteritems():
                self._list.append((key, value))
        elif isinstance(_dict_list, dict):
            for key, value in _dict_list.iteritems():
                self._list.append((key, value))
        elif isinstance(_dict_list, list):
            self._list.extend(_dict_list)
        else:
            warn(
                'The response head is initialized to None, '
                'because the param is not dict or list.', UserWarning
            )

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._list[key] = value
        else:
            key = http_key(key)
            for _id, (_key, _value) in enumerate(self._list):
                if _key == key:
                    self._list[_id] = (_key, str(_value))
                    break
            else:
                self.add(key, str(value))

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._list[item]
        item = http_key(item)
        for key, value in self._list:
            if key == item:
                return value

    def __delitem__(self, key):
        if isinstance(key, int):
            del self._list[key]
        else:
            key = http_key(key)
            for _id, _key, _value in enumerate(self._list):
                if key == _key:
                    del self._list[_id]

    def __iter__(self):
        return iter(self._list)

    def add(self, key, value):
        self._list.append((key, value))

    def head_to_list(self, charset='utf-8'):
        result = []
        for key, value in self:
            if isinstance(value, unicode):
                value = value.encode(charset)
            else:
                value = str(value)
            result.append((key, value))
        return result

    def __str__(self):
        string = ''
        for key, value in self.head_to_list():
            string += '%s: %s\r\n' % (key, value)
        return string


class EnvironHeader(object):
    """A data structure for request.environ.
    It will convert the input key to a standard key when users want to
    get the value of key
    """

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
                yield http_key(key[5:]), value
            elif key in ('CONTENT_LENGTH', 'CONTENT_TYPE'):
                yield http_key(key), value

    def handle_http_key(self, key):
        """content-type --> CONTENT_TYPE"""
        return key.upper().replace('-', '_')
