# -*- coding: utf-8 -*-
import os
import re
from setuptools import setup, find_packages


def _get_version():
    version_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'puck', '__init__.py')
    version_str = re.compile(r'.*version_info = \((.*?)\)', re.S).\
        match(open(version_path).read()).group(1)
    return version_str.replace(', ', '.')


setup(
    name='Pucks',
    version=_get_version(),
    url='https://github.com/EricQAQ/Puck',
    license='MIT',
    author='Eric Zhang',
    author_email='eric.pucker@gmail.com',
    description='A web micro-frame, quickly developing restful api.',
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=[
        'simplejson==3.8.2',
        'wheel==0.24.0',
        'itsdangerous==0.24.0',
        'redis==2.10.5',
    ],
)
