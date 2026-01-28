#!/usr/bin/env python
# coding:utf-8
# Author:  smeggingsmegger
# Purpose: setup
# Created: 2013-10-02
#
# The MIT License (MIT)

# Copyright (c) 2013 Scott Blevins

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return "File '%s' not found.\n" % fname

long_description = read("README.md")

if os.path.exists("README.txt"):
    long_description = open("README.txt").read()

setup(
    name="PyBambooHR",
    version="0.9.0",
    url="http://github.com/Reed-Schimmel/PyBambooHR",
    license="MIT",
    author="Reed Schimmel",
    author_email="reed.schimmel@example.com",
    description="A Python wrapper for the Bamboo HR API with SSO/Cookie authentication support",
    long_description=long_description + "\n" + read("CHANGES"),
    long_description_content_type="text/markdown",
    platforms="OS Independent",
    packages=["PyBambooHR"],
    include_package_data=True,
    install_requires=["requests", "xmltodict"],
    keywords=[
        "Bamboo",
        "HR",
        "BambooHR",
        "API",
        "SSO",
        "Okta",
        "Cookie",
        "Authentication",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
