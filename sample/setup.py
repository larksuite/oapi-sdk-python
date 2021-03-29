# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages

setup(
    name='larksuite-oapi-smaple',
    version='1.0.0',
    description='larksuite oapi python sample',
    author='rabbit',
    url='https://github.com/larksuite/oapi-sdk-python',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['crypto==1.4.1', 'pycryptodome>=3.0.0', 'attrs>=19.0.0,<20.0.0',
                      'requests>=2.20.0', 'typing;python_version<"3.5"'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ]
)
