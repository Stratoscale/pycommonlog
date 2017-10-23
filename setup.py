#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import codecs
import subprocess
from setuptools import find_packages, setup

URL = 'https://github.com/stratoscale/pycommonlog'
DESCRIPTION = 'pycommonlog repo'
NAME = os.path.basename(URL)
PKG_INFO = 'PKG-INFO'
AUTHOR = 'Stratoscale'
MAINTAINER = 'Ruslan Portnoy'
EMAIL = 'ruslan.portnoy@stratoscale.com'
DEPENDENCY_REGEX = re.compile(r"(?P<svn>git)\+(?P<url>https://github.com/\S+)/(?P<package>\S+)@(?P<version>[0-9a-f]+)#egg=(?P<egg>\S+)")


def _get_dependencies():
    dependencies_file = "dependencies.txt"
    result = []
    if not os.path.exists(dependencies_file):
        return result
    with open(dependencies_file) as f:
        for line in f.readlines():
            match = DEPENDENCY_REGEX.match(line.strip())
            if not match:
                continue
            dep = match.groupdict()
            result.append(dep)
    return result


def dependencies():
    result = []
    for dep in _get_dependencies():
        result.append("{svn}+{url}/{package}@{version}#egg={egg}-{version}".format(**dep))
    return result


def required():
    result = []
    # dependencies = _get_dependencies()
    # for dep in dependencies:
    #     result.append("{egg}=={version}".format(**dep))
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        return result
    with open("requirements.txt") as f:
        for line in f.readlines():
            if not line.strip():
                continue
            if line.strip().startswith('#'):
                continue
            result.append(line)
    return result


def data_files():
    site_packages_dir = os.path.join(sys.prefix, 'lib/python%s/site-packages' % sys.version[:3])
    pth_file = "{repo}.pth".format(repo=os.path.basename(URL))
    return [(site_packages_dir, [pth_file])]


def version():
    if os.path.exists(PKG_INFO):
        with open(PKG_INFO) as package_info:
            for key, value in (line.split(':', 1) for line in package_info):
                if key.startswith('Version'):
                    return value.strip()

    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


REQUIRED = required()
DEPENDENCIES = dependencies()
VERSION = version()
PACKAGES = find_packages('py')  # , exclude=('test',))
DATA_FILES = data_files()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    maintainer=MAINTAINER,
    url=URL,
    packages=PACKAGES,
    package_dir={
        '': 'py',
    },
    namespace_packages=[
        'strato',
        'strato.common',
    ],
    data_files=DATA_FILES,
    install_requires=REQUIRED,
    dependency_links=DEPENDENCIES,
    include_package_data=True,
    license='MIT',
    classifiers=[  # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
