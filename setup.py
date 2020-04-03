#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setup.py

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

about = {}
with open('./sleepscore/__about__.py') as f:
    exec(f.read(), about)

install_requires = [
    'numpy>=1.17.2',
    'visbrain>=0.4.5',
    'pyyaml',
    'docopt',
    'pandas',
    'tqdm',
    'pathlib',
    'tdt>=0.3.3'
]

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    install_requires=install_requires,
    packages=['sleepscore'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
    ]
)
