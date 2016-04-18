# -*- coding: utf-8 -*-
import urlparse
import tempfile

from .utils import parse_header_line, parse_dict_string


def parse_form_data(environ):
    """Parse data from environ when requests are PUT or POST. That is, this function will
    be called when the request is POST or PUT.
    1. When ' Content-Type = multipart/form-data ', there is always having files in the form.
    2. When ' Content-Type = application/x-www-form-urlencoded ', there is just Key-value pairs
    in the form

    :param environ: the WSGI environment

    :return (form, file)
            form is a list, which structure likes [(key1, val1), (key2, val2), (key3, val3), ...]
            file is a list, which structure likes [(name1, File object1), (name2, File object2), ...]
    """
    content_length = int(environ['CONTENT_LENGTH'] or 0)
    content_type, flag = parse_header_line(environ['CONTENT_TYPE'])

    if content_type == 'multipart/form-data':
        # POST or PUT Request submit a form, may have a file.
        form, file = parse_multipart(
            environ['wsgi.input'], content_length, flag.get('boundary')
        )

    elif content_type == 'application/x-www-form-urlencoded':
        # POST or PUT Request just submit a form, without a file.
        form = read_urlencoded(environ['wsgi.input'].read(content_length))
    else:
        pass

    return form, file


def read_urlencoded(s, keep_blank_values=0, strict_parsing=0):
    _list = []
    for key, value in urlparse.parse_qsl(s, keep_blank_values, strict_parsing):
        _list.append((key, value))
    return _list
