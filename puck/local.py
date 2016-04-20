# -*- coding: utf-8 -*-
try:
    from greenlet import getcurrent as get_current_greenlet
except ImportError:
    get_current_greenlet = int

from thread import get_ident as get_current_thread
from threading import Lock


if get_current_greenlet is int:  # Use thread
    get_ident = get_current_thread
else:   # Use greenlet
    get_ident = lambda: (get_current_thread(), get_current_greenlet())


class Local(object):
    __slots__ = ('__data__', '__lock__')

    def __init__(self):
        object.__setattr__(self, '__data__', {})
        object.__setattr__(self, '__lock__', Lock())

    def __iter__(self):
        return self.__data__.iteritems()

    def __getattr__(self, item):
        self.__lock__.acquire()
        try:
            try:
                return self.__data__[get_ident()][item]
            except KeyError:
                raise AttributeError(item)
        finally:
            self.__lock__.release()

    def __setattr__(self, key, value):
        self.__lock__.acquire()
        try:
            _id = get_ident()
            data = self.__data__
            if _id in data:
                data[_id][key] = value
            else:
                data[_id] = {key: value}
        finally:
            self.__lock__.release()

    def __delattr__(self, item):
        self.__lock__.acquire()
        try:
            try:
                del self.__data__[get_ident()][item]
            except KeyError:
                raise AttributeError(item)
        finally:
            self.__lock__.release()

    def __release__(self):
        self.__data__.pop(get_ident(), None)


class LocalStack(object):

    def __init__(self):
        self._local = Local()
        self._lock = Lock()

    def push(self, obj):
        self._lock.acquire()
        try:
            rv = getattr(self._local, 'stack', None)
            if rv is None:
                self._local.stack = rv = []
            rv.append(obj)
            return rv
        finally:
            self._lock.release()

    def pop(self):
        self._lock.acquire()
        try:
            stack = getattr(self._local, 'stack', None)
            if stack is None:
                return None
            elif len(stack) == 1:
                self._local.__release__()
                return stack[-1]
            else:
                stack.pop()
        finally:
            self._lock.release()

    @property
    def top(self):
        try:
            return self._local.stack[-1]
        except (AttributeError, IndexError):
            return None
