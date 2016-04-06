class Header(object):

    def __init__(self, environ):
        self.environ = environ

    def __len__(self):
        return len(dict(self))

    def __getattr__(self, item):
        item = item.upper().replace('-', '_')
        return self.environ['HTTP_' + item]
