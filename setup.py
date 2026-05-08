import re
from pathlib import Path

from setuptools import find_packages, setup

# Read VERSION from lark_oapi/core/const.py without importing the package,
# so editable installs work before runtime deps (httpx, websockets…) are set up.
_CONST = Path(__file__).parent / "lark_oapi" / "core" / "const.py"
_match = re.search(r'^VERSION\s*=\s*["\']([^"\']+)["\']', _CONST.read_text(encoding="utf-8"), re.M)
if not _match:
    raise RuntimeError("VERSION not found in lark_oapi/core/const.py")
VERSION = _match.group(1)

with open("README.md", mode="r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="lark-oapi",
    version=VERSION,
    description="Lark OpenAPI SDK for Python",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Wenbo Mao",
    author_email="maowenbo@bytedance.com",
    url="https://github.com/larksuite/oapi-sdk-python",
    license="MIT",
    packages=find_packages(
        exclude=["tests", "tests.*", "*.tests", "*.tests.*"],
    ),
    install_requires=[
        "requests>=2.25",
        "requests_toolbelt>=0.9",
        "pycryptodome>=3.9",
        "websockets>=11,<16",
        "httpx>=0.24,<1.0",
    ],
    extras_require={
        "aiohttp": ["aiohttp>=3.8"],
        "fastapi": ["fastapi>=0.100", "uvicorn>=0.23"],
        "flask": ["Flask>=2"],
        "test": ["pytest>=7", "pytest-asyncio>=0.21"],
    },
    python_requires=">=3.8",
    keywords=["Lark", "OpenAPI"],
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Source": "https://github.com/larksuite/oapi-sdk-python",
    },
)
