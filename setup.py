#!/usr/bin/env python3
from io import open
import os
import re

from setuptools import find_packages, setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('viewsets')


setup(
    name='django-viewsets',
    version=version,
    license='GPLv3',
    description='Django view classes, made easy.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Paul Wayper',
    author_email='paulway@mabula.net',
    # Note: Always better to log ideas and bugs via the GitHub project.
    packages=find_packages(exclude=['tests*']),
    install_requires=['django>=2.2'],
    python_requires'>=3.5',
    classifiers=[
        'Development Status :: 1 - Experimental',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
    ],
    project_urls={
        'Source': 'https://github.com/PaulWay/django-viewsets',
    },
)
