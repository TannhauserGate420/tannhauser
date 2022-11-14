#!/usr/bin/env python3

from setuptools import (
    setup,
    find_packages
)

from atomicswap.depends.config import tannhauser

with open(f"README.md", "r", encoding="utf-8") as readme:
    long_description: str = readme.read()

setup(
    name = "TannhauserGate",
    version = tannhauser['version'],
    description = "PoC Cross Chain Atomic Swap",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = "iizegrim",
    author_email = "iizegrim@protonmail.com",
    url = "https://github.com/TannhauserGate420/tannhauser",
    keywords = [
        "tannhausergate",
        "tannhauser",
        "atomicswap",
        "atomic",
        "swap",
        "bitcoin",
        "litecoin",
        "cryptocurrencies"
    ],
    python_requires = ">=3.7, <4",
    packages = find_packages(),
    install_requires = ['python-bitcoinrpc',
                    'python-bitcoinlib',
                    'python-litecoinlib',
                    'requests',
                    'emoji',
                    'PyQt5',
                    'stem',
                    'fake_http_header',
                    'PySocks'],
    entry_points = {
        "console_scripts": ["tannhauser = atomicswap.__main__:main"]
    },
    classifiers = [
          'Development Status :: 5 - Development',
          'Environment :: Console/Gui',
          'Intended Audience :: End Users/Desktop',
          'License :: GPL3',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python3',
          'Topic :: Atomicswap',
          ],
    include_package_data = True
)