# -*- coding: utf-8 -*-
import urlparse
import tempfile

from .utils import parse_header_line, parse_dict_string, parse_multipart_headers
from .data_structures import IterStream, File, Header


def valid_boundary(s, _vb_pattern="^[ -~]{0,200}[!-~]$"):
    """Valid the boundary string is valid or not. Reference cgi."""
    import re
    return re.match(_vb_pattern, s)


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
        _form, _file = parse_multipart(
            environ['wsgi.input'], content_length, flag.get('boundary')
        )

    elif content_type == 'application/x-www-form-urlencoded':
        # POST or PUT Request just submit a form, without a file.
        _form = read_urlencoded(environ['wsgi.input'].read(content_length))
        _file = None
    else:
        pass

    return _form, _file


def parse_multipart(file, content_length, boundary):
    """Parse file to form and file. Only called when ' Content-Type = multipart/form-data '

    The Request always like following block(leave out some unnecessary information.), Note
    that in HTTP header, usually using CRLF(\r\n) to end one line.

    POST http://www.example.com HTTP/1.1
    Content-Type:multipart/form-data; boundary=----WebKitFormBoundaryrGKCBY7qhFd3TrwA
    ------WebKitFormBoundaryrGKCBY7qhFd3TrwA        (-----------> real_boundary)
    Content-Disposition: form-data; name="text"

    title
    ------WebKitFormBoundaryrGKCBY7qhFd3TrwA
    Content-Disposition: form-data; name="file"; filename="chrome.png"
    Content-Type: image/png

    PNG ... content of chrome.png ...
    ------WebKitFormBoundaryrGKCBY7qhFd3TrwA--      (-----------> last_boundary)

    :param file: the file will be parsed. Usually the file is environ['wsgi.input']
    :param content_length: the length of the file
    :param boundary: the delimiter used in 'multipart/form-data', use this to split
                     key-value pairs

    :return (form, file)
            form is a list, which structure likes [(key1, val1), (key2, val2), (key3, val3), ...]
            file is a list, which structure likes [(name1, File object1), (name2, File object2), ...]
    """
    if not boundary:
        raise ValueError('Missing boundary, which is necessary.')
    if not valid_boundary(boundary):
        raise ValueError('Invalid boundary in multipart form.')
    real_boundary = '--' + boundary
    last_boundary = real_boundary + '--'

    file = IterStream(file, content_length)
    _form = Header(base=False)
    _file = Header(base=False)

    exit_flag = False

    line = file.next().rstrip()      # boundary

    if line != real_boundary:
        raise ValueError('Cannot found boundary in the start of data.')

    while not exit_flag:
        # sub_header = file.next()    # Content-Disposition: form-data; name="file"; filename="chrome.png"
        # sub_header = parse_header_line(sub_header)
        sub_header_list, sub_header_dict = parse_multipart_headers(file)
        if sub_header_list[0] != 'Content-Disposition: form-data':
            raise ValueError('Missing Content-Disposition header.')

        name = sub_header_dict.get('name')
        filename = sub_header_dict.get('filename')

        if filename is None:
            is_file = False
            container = []
            _write = container.append
        else:
            is_file = True
            # content_type = parse_dict_string(parse_header_line(file.next())[0]).get('Content-Type')
            content_type = parse_dict_string(sub_header_list[1])
            container = tempfile.TemporaryFile('wb+')
            _write = container.write

        buf = ''
        for line in file:
            if line[:2] == '--':
                line = line.rstrip()
                if line == real_boundary:
                    break
                if line == last_boundary:
                    exit_flag = True
                    break

            # if not line:    # blank line
            #     continue

            if buf:
                _write(buf)
                buf = ''

            if line[-2:] == '\r\n':
                buf = '\r\n'
                _write(line[:-2])
            elif line[-1:] == '\n':
                buf = '\n'
                _write(line[:-1])
            else:
                _write(line)

        if is_file:
            container.seek(0)
            _file.add(name, File(container, filename, content_type))
        else:
            _form.add(name, container)

    return _form, _file


def read_urlencoded(s, keep_blank_values=0, strict_parsing=0):
    """Called when ' Content-Type = application/x-www-form-urlencoded '.

    In this situation, the environ['wsgi.input'] like this:

        test=aaa&test1=bbb&test2=ccc

    So through method of parsing url can get the key-value pairs, and store the pairs
    in _form list.

    :param s: the string will be parsed, Usually is environ['wsgi.input']
    :param keep_blank_values: whether keep blank or not
    """
    _form = Header(base=False)
    for key, value in urlparse.parse_qsl(s, keep_blank_values, strict_parsing):
        _form.add(key, value)
    return _form
