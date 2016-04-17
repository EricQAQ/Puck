# -*- coding: utf-8 -*-
import urlparse


def generate_content_type(mime_type, charset):
    if mime_type.startswith('text/') or \
       mime_type == 'application/xml' or \
       (mime_type.startswith('application/') and mime_type.endswith('+xml')):
        mime_type = mime_type + '; charset' + charset
    return mime_type


def parse_content_type(content_type):
    """Parse Content-Type
        >>> parse_content_type('Content-Type: text/html; mimetype=text/html')
        ('Content-Type: text/html', {'mimetype': 'text/html'})

        >>> parse_content_type('Content-Type: multipart/form-data; boundary=BOUNDARY14355874244801')
        ('Content-Type: multipart/form-data', {'boundary': 'BOUNDARY14355874244801'})
    """
    parts = content_type.split(';')
    if len(parts) == 1:
        return parts[0], {}
    sp = parts[1].lstrip().split('=')

    return parts[0], {sp[0]: sp[1]}


def parse_multipart(file, content_length, boundary):
    pass


def read_urlencoded(s, keep_blank_values=0, strict_parsing=0):
    _list = []
    for key, value in urlparse.parse_qsl(s, keep_blank_values, strict_parsing):
        _list.append((key, value))
    return _list


def parse_form_data(environ):
    content_length = int(environ['CONTENT_LENGTH'] or 0)
    content_type, flag = parse_content_type(environ['CONTENT_TYPE'])

    if content_type == 'multipart/form-data':
        # POST or PUT Request submit a form, may have a file.
        form, file = parse_multipart(
            environ['wsgi.input'], content_length, flag.get('boundary')
        )
        pass

    elif content_type == 'application/x-www-form-urlencoded':
        # POST or PUT Request just submit a form, without a file.
        form = read_urlencoded(environ['wsgi.input'].read(content_length))
    else:
        pass

    return form
