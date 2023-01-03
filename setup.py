#!/usr/bin/env python3

from setuptools import (
    setup,
    find_packages
)

from atomicswap.depends.config import tannhauser

with open(f"README.md", "r", encoding="utf-8") as readme:
    long_description: str = readme.read()

setup(
    name = tannhauser['name'],
    version = tannhauser['version'],
    description = "P2P Cross Chain Atomic Swap",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = tannhauser['authors'],
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
                    'PySocks',
                    'cryptography'
    ],
    entry_points = {
        "console_scripts": ["tannhauser = atomicswap.__main__:main"]
    },
    classifiers = [
          'Development Status :: 3 - Alpha',
          'Environment :: X11 Applications :: Qt',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Utilities'
          ],
    include_package_data = True
)
