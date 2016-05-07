from .local import LocalStack


class Proxy(object):

    def __init__(self, local):
        # self.__local = local
        object.__setattr__(self, '__local', local)

    def _get_real_object(self):
        """Get the real object behind the Proxy. So that the users can
        operate the real things through the proxy
        """
        try:
            return object.__getattribute__(self, '__local')()
        except AttributeError:
            raise RuntimeError('no object bound to %s' % self.__name__)

    def __setattr__(self, key, value):
        setattr(self._get_real_object(), key, value)

    def __getattr__(self, item):
        return getattr(self._get_real_object(), item)

    def __getitem__(self, item):
        return self._get_real_object().__getitem__(item)

    def __setitem__(self, key, value):
        self._get_real_object().__setitem__(key, value)


request_stack = LocalStack()
current_app = Proxy(lambda: request_stack.top.app)
request = Proxy(lambda: request_stack.top.request)
session = Proxy(lambda: request_stack.top.session)
