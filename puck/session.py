# -*- coding: utf-8 -*-
import abc
import uuid
import time
from hashlib import sha1
import pickle
from itsdangerous import Signer, BadSignature


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
        print self.data

    def get(self, item):
        return self.__getitem__(item)

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            dict.__repr__(self.data)
        )


class PickleMixin:
    """Use pickle to serialize or unserialize the data."""

    serialization_method = pickle

    def unserialize(self, rawdata):
        return self.serialization_method.loads(rawdata)

    def serialize(self, data):
        return self.serialization_method.dumps(data)


class DictMixin:

    def serialize(self, data):
        pass

    def unserialize(self, rawdata):
        pass


class StoreSessionBase(object):

    @abc.abstractmethod
    def save_session(self, session, response, expire, path, domain, secure, httponly):
        pass

    @abc.abstractmethod
    def load_session(self, request, session_id):
        pass


class RedisSession(StoreSessionBase):
    """Use Redis to store sessions."""
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
        """Load session from the request.

        :param request: the request object
        :param key: the session name in cookies of the request.
        """
        session_id = request.cookies.get(key)
        signer = Signer(secret_key=self.secure_key)
        if session_id is not None:
            try:
                session_id = signer.unsign(session_id).decode('utf-8')
            except BadSignature:
                session_id = None
        if not session_id:  # the session is not exists, create a new session
            return self.make_session(self.key, self.secure_key)

        rawdata = self.redis.get(session_id)      # str
        if not rawdata:
            rawdata = self.redis.hgetall(session_id)  # dict

        if not rawdata:    # the session is not exists, create a new session
            return self.make_session(self.key, self.secure_key)

        data = self.unserialize(rawdata)
        return SessionBase(key=self.key, data=data, secure_key=self.secure_key)

    def save_session(self, session, response, expire=None, path=None,
                     domain=None, secure=None, httponly=False):
        """Save the session into the redis and update the session_id"""
        session_id = session.get(self.key)
        serialized_session = self.serialize(session.data)

        if not expire:
            serialied_type = self.redis.set   # 0: string, 1: dict
            if isinstance(serialized_session, dict):
                serialied_type = self.redis.hmset

            serialied_type(session_id, serialized_session)

        else:
            pipe = self.redis.pipeline()
            serialied_type = pipe.set
            if isinstance(serialized_session, dict):
                serialied_type = pipe.hmset

            serialied_type(session_id, serialized_session)
            pipe.expire(session_id, expire)
            pipe.execute()

        signer = Signer(self.secure_key)
        session_id = signer.sign(session_id.encode('utf-8')).decode('utf-8')

        response.set_cookies(
            key=self.key, value=session_id, expires=expire, path=path,
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
