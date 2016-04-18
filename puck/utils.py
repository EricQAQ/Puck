# -*- coding: utf-8 -*-


def generate_content_type(mime_type, charset):
    if mime_type.startswith('text/') or \
       mime_type == 'application/xml' or \
       (mime_type.startswith('application/') and mime_type.endswith('+xml')):
        mime_type = mime_type + '; charset' + charset
    return mime_type


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


def parse_dict_string(s):
    """
        >>> parse_dict_string('Content-Type: text/html')
        {'Content-Type': 'text/html'}
    """
    parts = s.split(':')
    return {parts[0]: parts[1][1:]}
