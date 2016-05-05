# -*- coding: utf-8 -*-


def generate_content_type(mime_type, charset):
    if mime_type.startswith('text/') or \
       mime_type == 'application/xml' or \
       (mime_type.startswith('application/') and mime_type.endswith('+xml')):
        mime_type = mime_type + '; charset' + charset
    return mime_type


def _remove_end_characters(line):
    """Removes line ending characters"""
    if line[-2:] == '\r\n':
        return line[:-2], True
    elif line[-1:] in '\r\n':
        return line[:-1], True
    return line, False


def parse_header_line(content_type):
    """Parse One Line of Header
        >>> parse_header_line('Content-Type: text/html; mimetype=text/html')
        ('Content-Type: text/html', {'mimetype': 'text/html'})

        >>> parse_header_line('Content-Type: multipart/form-data; boundary=BOUNDARY14355874244801')
        ('Content-Type: multipart/form-data', {'boundary': 'BOUNDARY14355874244801'})

        >>> parse_header_line('Content-Disposition: form-data; name="file"; filename="chrome.png"')
        ('Content-Disposition: form-data', {'name': 'file', 'filename': 'chrome.png'})
    """
    parts = content_type.split(';')
    if len(parts) == 1:
        return parts[0], {}
    # sp = parts[1].lstrip().split('=')
    _dict = {}
    for part in parts[1:]:
        sp = part.lstrip().split('=')
        if sp[1].startswith('"') and sp[1].endswith('"'):
            sp[1] = sp[1][1:-1]
        _dict[sp[0]] = sp[1]

    return parts[0], _dict


def parse_multipart_headers(iterable):
    """Parse multipart header. Only called when ' Content-Type = multipart/form-data '.
    It can parse the sub headers. For Example:

        Content-Disposition: form-data; name="file"; filename="chrome.png"
        Content-Type: image/png
        ----THE BLANK LINE----

        this head block will be parsed into:
        (
            [
                'Content-Disposition: form-data',
                'Content-Type: image/png'
            ],
            {'name': 'test', 'filename': 'chrome.png'}
        )

    :param iterable: a object which is iterable. Always environ['wsgi.input'].

    :return tuple: (_list, _dict), _list has two string, One is Disposition, another is Type.
    """
    _list = []
    _dict = {}
    for line in iterable:
        line, end_char = _remove_end_characters(line)
        if not end_char:
            raise ValueError('unexpected end of line in multipart header')
        if not line:
            break
        tmp_string, tmp_dict = parse_header_line(line)
        _list.append(tmp_string)
        _dict = tmp_dict if tmp_dict else _dict
    return _list, _dict


def parse_dict_string(s):
    """
        >>> parse_dict_string('Content-Type: text/html')
        {'Content-Type': 'text/html'}
    """
    parts = s.split(':')
    return {parts[0]: parts[1][1:]}


def lazy_property(func):
    name = '__lazy__' + func.__name__

    @property
    def lazy(self):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self)
            setattr(self, name, value)
            return value
    return lazy
