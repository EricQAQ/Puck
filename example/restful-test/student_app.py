# -*- coding: utf-8 -*-
from puck import Puck, api_response
from puck.restful import Param, RequestParamParser
from puck.restful import variable_parser


class Student(RequestParamParser):
    name = Param('name', str, required=True)
    age = Param('age', int, required=True)
    sex = Param('sex', int, required=True)
    address = Param('address', str)


app = Puck()


@app.route('/student', methods=['POST'])
@variable_parser(Student)
def test(variable_data):
    return api_response(data=variable_data)


if __name__ == '__main__':
    app.run()
