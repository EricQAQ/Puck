import re
from urllib import urlencode

# this regular expression for matching dynamic routing rule.
# Ex: /example/<int:test>
# this RE string can match this part: "<int:test>"
_rule_re = re.compile(r'''
    <
    (?:
        (?P<type>int|str|float)   # the type of variable
        \:
    )?
    (?P<variable>[a-zA-Z][a-zA-Z0-9_]*)         # the name of variable
    >
''', re.VERBOSE)

_type_map = {
    'int': r'\d+',
    'float': r'\d+(?:\.\d+)',
    'str': r'.+',
}


def parse_rule(rule):
    rule = rule.rstrip('/').lstrip('/')
    rule_list = rule.split('/')
    for item in rule_list:
        m = _rule_re.match(item)
        if m is None:
            yield None, None, item
        else:
            data_dict = m.groupdict()
            yield data_dict['type'], data_dict['variable'], None


class Rule(object):

    def __init__(self, rule_str, rule_name=None, methods=('GET',)):
        if not rule_str.startswith('/'):
            raise ValueError('urls must start with a leading slash')
        # the origin url rule string.
        self.rule = rule_str

        # the list to store the variable-type pair.
        # Can use this list to build url. Example:
        # [('example', None), ('test', <type 'int'>), ('test2', <type 'int'>)]
        # we can use this list to build url:
        # /example/<int:test>/<int:test2>
        self.match_order = []

        # the name of the rule, it is a flag to mapping a function
        self.rule_name = rule_name

        # the support methods of the rule
        self.methods = set(item.upper() for item in methods)

        # flag for judge whether the rule is a dynamic rule
        self.dynamic = False

        # if the rule is a dynamic rule, use this param to store the variables
        self.type_variable = {}

        self._analysize_rule(self.rule)

        # the url like "/example/{test}/{test2}"
        # through this param can build the real url if given the relative params.
        self.base_rule = self.build_base_rule()

        # the url in Regular Expression.
        self.rule_re = re.compile(self.complie_rule())

    def complie_rule(self):
        rule_re = '^/'
        for variable, _type in self.match_order:
            if not _type:
                rule_re += variable + '/'
            else:
                type_replace = _type_map[_type.__name__]
                rule_re += r'(?P<{variable}>{type_replace})/'.format(
                    variable=variable, type_replace=type_replace
                )
        if rule_re == '^//':
            return '^/$'
        return rule_re.rstrip('/') + '$'

    def build_base_rule(self):
        """To build the base url. Example:
            >>>r = Rule('/example/<int:test>/<int:test2>', methods=['GET, POST'])
            >>>print r.build_base_rule()
        Output:
            /example/{test}/{test2}
        """
        if not self.dynamic:
            return self.rule
        rule = '/'
        for variable, _type in self.match_order:
            if not _type:
                rule += variable + '/'
            else:
                rule += '{' + variable + '}' + '/'
        return rule.rstrip('/')

    def build_url(self, **kwargs):
        """According the params to build full url. Example:
            " /example/{id}  -> /example/1"
        """
        variable_dict = self.get_variables()
        unknown_variable = set()
        # check type and find out unknown variable
        for key, value in kwargs:
            if key in variable_dict and \
                    not isinstance(value, variable_dict[key]):
                raise TypeError
            elif key not in variable_dict:
                unknown_variable.add(key)
        url = self.base_rule.format(**kwargs)
        if unknown_variable:
            url += '?' + urlencode(
                {k: kwargs[k] for k in unknown_variable}
            )
        return url

    def get_variables(self):
        _dict = {}
        for varibale, _type in self.match_order:
            if _type is not None:
                _dict[varibale] = _type
        return _dict

    def _analysize_rule(self, rule):
        """Analysize the url, get and save the key-value dict. Example:
            >>>s = '/example/<int:t>/test'
            >>>r3 = Rule(s)
            >>>r.build_rule()
            >>>print r3.dynamic
            >>>print r3.type_variable
            >>>print r3.match_order
        Output:
            True
            {'t': <type 'int'>}
            [('example', None), ('t', <type 'int'>), ('test', None)]
        """
        for _type, variable, rule_item in parse_rule(rule):
            if _type is None:
                if variable is None:
                    # not match any variables, static rule
                    self.match_order.append((rule_item, None))
                else:
                    # dynamic rule, setting default type
                    self.type_variable[variable] = str
                    self.dynamic = True
                    self.match_order.append((variable, str))
            else:
                self.dynamic = True
                if _type == 'int':
                    self.type_variable[variable] = int
                elif _type == 'str':
                    self.type_variable[variable] = str
                else:
                    self.type_variable[variable] = float
                self.match_order.append(
                    (variable, self.type_variable[variable])
                )

    def __str__(self):
        pass


class Router(object):

    def __init__(self):
        self.route_to_name = []
        self.name_to_func = []

    def add(self, url, handler, **kwargs):
        """Add new url rule. Called by add_route in Puck.

        :param url: the url rule will be added.
        :param handler: the relative function to the url rule. That is, if receiving a request to
                        THE url, it will be mapped to THE function to handle the request.
        :param methods: the methods that allows to this url.
        """
        rule_name = kwargs['rule_name']
        methods = set(method.upper() for method in kwargs['methods'])
        if 'GET' in methods and 'HEAD' not in methods:
            methods.add('HEAD')
        rule = Rule(rule_str=url, rule_name=rule_name, methods=methods)

        self.route_to_name.append((rule_name, rule))
        self.name_to_func.append((rule_name, handler))

    def url_for(self, rule_name, **kwargs):
        """According to the giving rule name(default value is function name)
        and params, build the url which matches the function."""
        for _rule_name, rule in self.route_to_name:
            if _rule_name == rule_name:
                return rule.build_url(**kwargs)
        return ''

    def match_url(self, url):
        """According the request url, to matching the handler.
        :return: (function, methods, params)"""
        for rule_name, rule in self.route_to_name:
            m = rule.rule_re.match(url)
            if m is not None:
                func = self._search_func(rule_name)
                return func, rule.methods, m.groupdict()
        return None, None, None

    def _search_func(self, name):
        for _name, func in self.name_to_func:
            if name == _name:
                return func
        return None
