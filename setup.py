from distutils.core import setup
from setuptools import find_packages, find_namespace_packages

setup(
    name='lark-oapi',
    version='1.0.3',
    description='Lark OpenAPI SDK for Python',
    author='Wenbo Mao',
    author_email='maowenbo@bytedance.com',
    url='https://github.com/larksuite/oapi-sdk-python',
    packages=find_packages(),
    install_requires=['requests', 'requests_toolbelt'],
    python_requires=">=3.8",
    keywords=['Lark', 'OpenAPI'],
    include_package_data=True,
)
