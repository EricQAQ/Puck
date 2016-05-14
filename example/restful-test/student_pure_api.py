# -*- coding: utf-8 -*-
from puck import Puck, api_response
from puck.restful import Param, RequestParamParser
from puck.restful import variable_parser


class Student(RequestParamParser):
    name = Param('name', str, required=True)
    age = Param('age', int, required=True)
    sex = Param('sex', int, required=True)
    address = Param('address', str)


app = Puck(use_api=True)


class StudentAPI(object):

    @variable_parser(Student)
    def post(self, i):
        variable_data = getattr(self, 'variable_data')
        return api_response(data=variable_data)

app.add_route('/stu/<int:i>', resource=StudentAPI())


if __name__ == '__main__':
    app.run()
