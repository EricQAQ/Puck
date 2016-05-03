# -*— coding:utf-8 -*-
from warnings import warn

CHUNK_SIZE = 1024 * 10


def http_key(key):
    """content-type --> Content-Type"""
    return key.replace('_', '-').title()


class Header(object):
    """Store response header, Also be used in request._form and request._file.
    Header class support three ways to initialize:
    1. Supply a dict object
    2. DO NOT Supply a dict or list object, but gives key-value pairs
    3. Supply a list object

    Data-structure:
    self._list = [(key1, value1), (key2, value2), ...]
    """
    def __init__(self, _dict_list=None, base=True, *args, **kwargs):
        # self._list = [(key, value), (key, value), ...]
        self._list = []

        # Flag for judge whether this class is used to be a instance of HTTP Header.
        # Currently, it is useful when Header class is used in request._form and request._file
        self.base = base

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
            key = http_key(key) if self.base else key
            for _id, (_key, _value) in enumerate(self._list):
                if _key == key:
                    self._list[_id] = (_key, str(_value))
                    break
            else:
                self.add(key, str(value))

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._list[item]
        item = http_key(item) if self.base else item
        for key, value in self._list:
            if key == item:
                return value

    def __delitem__(self, key):
        if isinstance(key, int):
            del self._list[key]
        else:
            key = http_key(key) if self.base else key
            for _id, _key, _value in enumerate(self._list):
                if key == _key:
                    del self._list[_id]

    def __iter__(self):
        return iter(self._list)

    def add(self, key, value):
        self._list.append((key, value))

    def get(self, key):
        key = http_key(key) if self.base else key
        for _key, _value in self._list:
            if _key == key:
                return _value
        return None

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


class IterStream(object):
    """
    Make an instance of the object, which can get the data which size is limited.
    """
    def __init__(self, stream, end):
        """Init the IterStream.

        :param stream: the data stream
        :param end: the size of the data
        """
        self._pos = 0
        self.end = end
        self._read = stream.read
        self._readline = stream.readline

    def __iter__(self):
        return self

    def next(self):
        line = self.readline()
        if not line:
            raise StopIteration()
        # if line[-2:] == '\r\n':
        #     return line[:-2]
        return line

    def read(self, size=CHUNK_SIZE):
        """Read the stream, if the size is given, read the constant size data."""
        if self._pos >= self.end:
            return ''
        read = self._read(min(self.end-self._pos, size))
        self._pos += len(read)
        return read

    def readline(self, size=None):
        if self._pos >= self.end:
            return ''
        if size is None:
            size = self.end - self._pos
        else:
            size = min(self.end-self._pos, size)
        line = self._readline(size)

        self._pos += len(line)
        return line

    @property
    def is_exhausted(self):
        return self._pos >= self.end


class File(object):

    def __init__(self, stream, file_name, content_type='application/octet-stream'):
        self.file_name = file_name
        self.stream = stream
        self.content_type = content_type

    def read_data_from_stream(self, stream, chunk_size=CHUNK_SIZE):
        """Get the constant size data from the stream. It is a generater."""
        stream.seek(0)
        while True:
            data = stream.read(chunk_size)
            if not data:
                break
            yield data

    def create(self, destination):
        """Create a new file, and set data of the stream into the file."""
        with open(destination, 'w+b') as f:
            for data in self.read_data_from_stream(self.stream):
                f.write(data)
        self.close()

    def close(self):
        """Close the underlying file if possible."""
        try:
            self.stream.close()
        except:
            pass

    def __repr__(self):
        return '<%s: %r (%r)>' % (
            self.__class__.__name__,
            self.file_name,
            self.content_type
        )
