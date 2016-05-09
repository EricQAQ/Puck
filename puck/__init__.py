# -*- coding: utf-8 -*-

"""
    A lightweight WSGI web framework. Quickly to create restful api.

    Puck
    -----------------------------------

    The MIT License (MIT)

    Copyright (c) 2016 Eric Zhang

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

version_info = (0, 1, 2)

__author__ = 'Eric Zhang'
__version__ = ".".join([str(v) for v in version_info])
__email__ = 'eric.pucker@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2016 Eric in NEU'


from .app import Puck
from .helper import jsonify, api_response, make_response
from .request import Request
from .response import Response
from .globals import current_app, request, session
from .exceptions import HTTPException
