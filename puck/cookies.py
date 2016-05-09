# -*- coding: utf-8 -*-
from datetime import datetime
from time import time, gmtime
from Cookie import SimpleCookie, Morsel

from itsdangerous import Signer, BadSignature

from .utils import parse_dict_string


def set_cookie_date(expires):
    """Outputs a string in the format " Thu, DD-MM-YYYY HH:MM:SS GMT "."""
    if isinstance(expires, datetime):
        expires = expires.utctimetuple()
    elif isinstance(expires, (int, float, long)):
        expires = gmtime(expires)

    return '%s, %02d-%s-%s %02d:%02d:%02d GMT' % (
        ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')[expires.tm_wday],
        expires.tm_mday,
        ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
         'Oct', 'Nov', 'Dec')[expires.tm_mon - 1],
        str(expires.tm_year), expires.tm_hour, expires.tm_min, expires.tm_sec
    )


def parse_cookie(environ):
    """Parse the cookie from request.

    :return A dict(key: cookie name, value: the cookie value, not the instance of Morsel)
            The cookies should be like this:
            {'session_id': '1', 'test': 'xxx'}

    """
    raw_cookie = SimpleCookie(environ.get('HTTP_COOKIE', ''))
    cookie = {}
    for key, value in raw_cookie.iteritems():
        # cookie[key] = value.OutputString()[len(key)+1:]
        cookie_str = value.OutputString()
        k, v = parse_dict_string(cookie_str, split_sign='=', use_tuple=True)
        cookie[k] = v
    return cookie


def generate_cookie(key, value, expires=None, path='/', domain=None,
                    max_age=None, secure=None, httponly=False):
    """Generate a cookie. Called by the function of set_cookie(). The params are
    the same as the Morsel object in the Cookie which is a Python Standard Library.

    :param key: the name of the cookie to be set
    :param value: the value of the cookie
    :param expires: should be a `datetime` object or UNIX timestamp.
    :param path: limit the cookie to the given path.
    :param domain: set a cross-domain cookie. Example:
                   domain=".example.com", it will set the cookie that is
                   readable by the domain "www.example.com"
    :param max_age: should be a number of seconds or None.
    :param secure: The cookie will only be available via HTTPS

    :return morsel: Type is Morsel.
    """

    morsel = Morsel()
    if key is not None:
        morsel.set(key, value, value)

    if expires is not None:
        if not isinstance(expires, basestring):
            expires = set_cookie_date(expires)
        morsel['expires'] = expires
    elif max_age is not None:
        morsel['expires'] = set_cookie_date(time() + max_age)

    for key, value in (('path', path), ('domain', domain),
                       ('secure', secure), ('httponly', httponly)):
        if value is not None and value is not False:
            morsel[key] = value

    return morsel


def cookie_serialize(secure_key, session_id, expire):
    """Serialize the cookie. Set the expire_time timestamp into the cookie"""
    signer = Signer(secure_key)
    session_data = session_id.encode('utf-8') + '&' + str(expire)

    session_data = signer.sign(session_data).decode('utf-8')
    return session_data


def cookie_unserialize(session_data, secure_key):
    """Unserialize the cookie: separate the session_id and expire_time timestamp."""
    signer = Signer(secret_key=secure_key)
    try:
        session_data = signer.unsign(session_data).decode('utf-8')
    except BadSignature:
        session_data = None
    if not session_data:
        return None, None
    session_id, session_expire = session_data.split('&')
    return session_id, session_expire

