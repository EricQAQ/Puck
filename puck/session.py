# -*- coding: utf-8 -*-
import abc
import uuid
import time
from datetime import datetime
from hashlib import sha1
import pickle
from itsdangerous import Signer, BadSignature

from .utils import get_utc_time_stamp
from .cookies import cookie_serialize, cookie_unserialize


class SessionBase(object):
    """The session class."""

    def __init__(self, secure_key, key, data=None):
        self.key = key
        self.data = dict(data) if data else dict()
        self.secure_key = secure_key
        self.data.__setitem__(self.key, self._get_session_id())

    def _generate_session_id(self):
        signer = Signer(self.secure_key)
        tmp = sha1('%s%s' % (time.time(), uuid.uuid4())).hexdigest()
        return signer.sign(tmp)

    def _get_session_id(self):
        """Get session_id from data or create a new id."""
        if self.data.get(self.key, None):
            return self.data[self.key]
        return self._generate_session_id()

    def __getitem__(self, item):
        return self.data.get(item)

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, item):
        return self.__getitem__(item)

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            dict.__repr__(self.data)
        )


class PickleMixin:
    """A mixin for classes which can use pickle to
    serialize or unserialize the data."""

    serialization_method = pickle

    def unserialize(self, rawdata):
        return self.serialization_method.loads(rawdata)

    def serialize(self, data):
        return self.serialization_method.dumps(data)


class DictMixin:
    """A mixin for classes which can use dict to
    serialize or unserialize the data."""

    def serialize(self, data):
        """Convert the data into a dict."""
        if data:
            try:
                return dict(data)
            except (TypeError, ValueError):
                raise ValueError('The data cannot be converted into a dict.')

    def unserialize(self, rawdata):
        """Convert the data into a dict."""
        if rawdata:
            try:
                return dict(rawdata)
            except (TypeError, ValueError):
                raise ValueError('The data cannot be converted into a dict.')


def get_expire_seconds(session_expire):
    """Get the expire seconds.

    :param session_expire: the session expire time
    """
    session_expire = get_utc_time_stamp(int(session_expire))
    current_timestamp = get_utc_time_stamp(datetime.utcnow())
    seconds = session_expire - current_timestamp
    return seconds


class StoreSessionBase(object):
    """The base class for redis serialization.
    The sub class should be overridden following methods:

    - save_session()
    - load_session()
    """

    @abc.abstractmethod
    def save_session(self, session, response, expire,
                     path, domain, secure, httponly):
        """Saves the session in a cookie on response object if it needs
        updates.

        :param session: the session to be saved.
        :param response: a response object that has a
                         BaseResponse.set_cookie method.
        :param expire: should be a `datetime` object or UNIX timestamp.
        :param path: limit the cookie to the given path.
        :param domain: set a cross-domain cookie. Example:
                       domain=".example.com", it will set the cookie that is
                       readable by the domain "www.example.com"
        :param secure: The cookie will only be available via HTTPS.
        """
        pass

    @abc.abstractmethod
    def load_session(self, request, key):
        """Loads the session from the request.
        If the session is not exist, create a new session and return it.

        :param request: a request object that has a `cookies` attribute.
        :param key: the name of the session id in cookie.
        """
        pass


class RedisSession(StoreSessionBase):
    """Use Redis to store sessions."""
    # use hash type to store the session
    hash_type = 'hash'

    # use string type to store the seesion
    string_type = 'string'

    def __init__(self, redis_host, redis_port, secure_key, key,
                 redis_db=0, redis_pw=None, use_pool=False, redis=None, max_conn=None):
        """Init redis session.

        :param redis_host: the host of redis
        :param redis_port: the port of redis
        :param redis_db: the db number will be used in redis
        :param redis_pw: the password of the redis
        :param use_pool: whether use connection pool or not
        :param redis: the StrictRedis object
        :param max_conn: the number of the connections, only usable when use_pool=True
        """
        # super(RedisSession, self).__init__(key=key, data=data, secure_key=secure_key)
        if redis is None:
            from redis import StrictRedis

            if use_pool and max_conn is not None:
                from redis import ConnectionPool
                pool = ConnectionPool(
                    host=redis_host, port=redis_port, max_connections=max_conn)
                redis = StrictRedis(connection_pool=pool)
            else:
                redis = StrictRedis(
                    host=redis_host, port=redis_port, db=redis_db, password=redis_pw)
        self.key = key
        self.secure_key = secure_key
        self.redis = redis

    def make_session(self, key, secure_key):
        """Make a new session"""
        return SessionBase(key=key, secure_key=secure_key)

    def load_session(self, request, key):
        """Load session from the request. If the session is not exist, create a new session.

        :param request: the request object
        :param key: the session name in cookies of the request.
        """
        session_raw = request.cookies.get(key)

        if session_raw:
            session_id, session_expire = cookie_unserialize(session_raw, self.secure_key)
        else:
            session_id = session_expire = None
        if not session_id:  # the session is not exists, create a new session
            return self.make_session(self.key, self.secure_key)

        # the flag that whether delete the key from redis
        del_flag = False

        if session_expire:  # has expire time
            if get_expire_seconds(session_expire) < 0:    # the session has expired, del from redis
                del_flag = True

        data_type = self.redis.type(session_id)
        if data_type == self.string_type:
            rawdata = self.redis.get(session_id)      # str
        elif data_type == self.hash_type:
            rawdata = self.redis.hgetall(session_id)  # dict
        else:
            rawdata = None

        if rawdata is not None and del_flag:    # del from redis
            self.redis.delete(session_id)
            rawdata = None

        # the session is not exists, create a new session
        if not rawdata:
            return self.make_session(self.key, self.secure_key)

        data = self.unserialize(rawdata)
        return SessionBase(key=self.key, data=data, secure_key=self.secure_key)

    def save_session(self, session, response, expire=None, path=None,
                     domain=None, secure=None, httponly=False):
        """Save the session into the redis and update the session_id"""
        session_id = session.get(self.key)
        serialized_session = self.serialize(session.data)

        if expire:
            expire = get_utc_time_stamp(expire)
            expire_second = get_expire_seconds(expire)

        if not expire:
            serialied_type = self.redis.set   # default: string
            if isinstance(serialized_session, dict):
                serialied_type = self.redis.hmset
            # store the session into redis
            serialied_type(session_id, serialized_session)

        else:
            pipe = self.redis.pipeline()
            serialied_type = pipe.set
            if isinstance(serialized_session, dict):
                serialied_type = pipe.hmset

            serialied_type(session_id, serialized_session)
            pipe.expire(session_id, expire_second)
            pipe.execute()

        session_data = cookie_serialize(self.secure_key, session_id, expire)

        response.set_cookies(
            key=self.key, value=session_data, expires=expire, path=path,
            domain=domain, secure=secure, httponly=httponly
        )


class RedisPickleSession(PickleMixin, RedisSession):
    """
    1. Use Pickle to serialize the session data.
    2. And use redis to store the sessions.
    """
    pass


class RedisDictSession(DictMixin, RedisSession):
    """
    1. Use dict to serialize the session data.
    2. And use redis to store the sessions.
    """
    pass
