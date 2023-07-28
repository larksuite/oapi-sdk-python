from distutils.core import setup

from setuptools import find_packages

from lark_oapi.core import VERSION

setup(
    name='lark-oapi',
    version=VERSION,
    description='Lark OpenAPI SDK for Python',
    author='Wenbo Mao',
    author_email='maowenbo@bytedance.com',
    url='https://github.com/larksuite/oapi-sdk-python',
    packages=find_packages(),
    install_requires=['requests', 'requests_toolbelt', 'flask', 'pycryptodome'],
    python_requires=">=3.8",
    keywords=['Lark', 'OpenAPI'],
    include_package_data=True,
)
