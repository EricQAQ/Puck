from .local import LocalStack


class Proxy(object):

    def __init__(self, func):
        self.func = func

    def __getattr__(self, item):
        return getattr(self.func(), item)


request_stack = LocalStack()
current_app = Proxy(lambda: request_stack.top.app)
request = Proxy(lambda: request_stack.top.request)
