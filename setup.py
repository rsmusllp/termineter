#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 shiftwidth=4 noexpandtab
#
#  setup.py
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the project nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os
import sys

base_directory = os.path.dirname(__file__)

try:
	from setuptools import setup, find_packages
except ImportError:
	print('This project needs setuptools in order to build. Install it using your package')
	print('manager (usually python-setuptools) or via pip (pip install setuptools).')
	sys.exit(1)

try:
	import pypandoc
	long_description = pypandoc.convert(os.path.join(base_directory, 'README.md'), 'rst')
except (ImportError, OSError):
	print('The pypandoc module is unavailable, can not generate the long description', file=sys.stderr)
	long_description = None

DESCRIPTION = """\
Termineter is a Python framework which provides a platform for the security \
testing of smart meters.\
"""

setup(
	name='termineter',
	version='1.0.4',
	author='Spencer McIntyre',
	author_email='smcintyre@securestate.com',
	maintainer='Spencer McIntyre',
	description=DESCRIPTION,
	long_description=long_description,
	url='https://github.com/securestate/termineter',
	license='BSD',
	# these are duplicated in requirements.txt
	install_requires=[
		'crcelk>=1.0',
		'pluginbase>=0.5',
		'pyasn1>=0.1.7',
		'pyserial>=2.6',
		'smoke-zephyr>=1.2',
		'tabulate>=0.8.1',
		'termcolor>=1.1.0'
	],
	package_dir={'': 'lib'},
	packages=find_packages('lib'),
	package_data={
		'': ['data/*'],
	},
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Topic :: Security'
	],
	scripts=['termineter']
)
