# -*- coding: utf-8 -*-
import time
import datetime

# the days from 0001-01-01 to 1970-01-01
_epoch_day = datetime.date(1970, 1, 1).toordinal()


def local_time_2_utc(l_time):
    """Convert the local time into utc time

    :return a datetime object.
    """
    if isinstance(l_time, datetime.datetime):
        l_time = time.mktime(l_time.timetuple())
    return datetime.datetime.utcfromtimestamp(l_time)


def get_after_input_time(input_time):
    """Get the datetime after the input_time.

    :param input_time: a tuple:(Year, Month, Day, Hour, Minute, Second)

    :return an instance of datetime
    """
    current_time = datetime.datetime.now()
    c_year, c_month, c_day, c_hour, c_minute, c_second = current_time.timetuple()[:6]
    year, month, day, hour, minute, second = input_time
    return datetime.datetime(
        year+c_year, month+c_month, day+c_day,
        hour+c_hour, minute+c_minute, second+c_second
    )


def get_utc_time_stamp(expire):
    """
    Convert the expire time into seconds from
    1970-01-01(Y: 1970, M: 1, D: 1) to expire time(the param)

    :param expire: int, float, long, datetime, dict

    :return the seconds
    """
    if isinstance(expire, (int, float, long)):
        return int(expire)
    if isinstance(expire, datetime.datetime):
        expire = expire.utctimetuple()
    year, month, day, hour, minute, second = expire[:6]
    day = datetime.date(year, month, day).toordinal() - _epoch_day
    seconds = ((day * 24 + hour) * 60 + minute) * 60 + second
    return seconds


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


def parse_header_line(content_type, split_sign=';'):
    """Parse One Line of Header
        >>> parse_header_line('Content-Type: text/html; mimetype=text/html')
        ('Content-Type: text/html', {'mimetype': 'text/html'})

        >>> parse_header_line('Content-Type: multipart/form-data; boundary=BOUNDARY14355874244801')
        ('Content-Type: multipart/form-data', {'boundary': 'BOUNDARY14355874244801'})

        >>> parse_header_line('Content-Disposition: form-data; name="file"; filename="chrome.png"')
        ('Content-Disposition: form-data', {'name': 'file', 'filename': 'chrome.png'})

    :param content_type: the string that will be parsed
    :param split_sign: the split char

    :return a tuple: (string, dict) the first one is a string, the second one is a dict
    """
    parts = content_type.split(split_sign)
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


def parse_dict_string(s, split_sign=':', use_tuple=False):
    """
        >>> parse_dict_string('Content-Type: text/html')
        {'Content-Type': 'text/html'}

    :param s: the string that will be parsed
    :param split_sign: the split char
    :param use_tuple: whether return a tuple, if True, return a tuple, else return a dict
    """
    parts = s.split(split_sign)
    if use_tuple:
        return parts[0], parts[1].lstrip()
    return {parts[0]: parts[1].lstrip()}


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
