#!/usr/bin/python3 -B
# vim: tabstop=4 softtabstop=4 shiftwidth=4 noexpandtab
#
#  setup.py
#
#  Copyright 2016 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys

base_directory = os.path.dirname(__file__)
lib_directory = os.path.join(base_directory, 'lib')
if os.path.isdir(os.path.join(lib_directory, 'termineter')):
	sys.path.insert(0, lib_directory)

from termineter import __version__

try:
	from setuptools import setup, find_packages
except ImportError:
	print('Termineter needs setuptools in order to build. Install it using')
	print('your package manager (usually python-setuptools) or via pip (pip')
	print('install setuptools).')
	sys.exit(1)

try:
	import pypandoc
	long_description = pypandoc.convert(os.path.join(base_directory, 'README.md'), 'rst')
except (ImportError, OSError):
	long_description = None

DESCRIPTION = """\
Termineter is a Python framework which provides a platform for the security \
testing of smart meters.\
"""

setup(
	name='termineter',
	version=__version__,
	author='Spencer McIntyre',
	author_email='smcintyre@securestate.com',
	maintainer='Spencer McIntyre',
	description=DESCRIPTION,
	long_description=long_description,
	url='https://github.com/securestate/termineter',
	license='GPLv3',
	install_requires=(
		'crcelk>=1.0',
		'pyasn1>=0.1.7',
		'pyserial>=2.6',
		'smoke-zephyr==1.0.2'
	),
	package_dir={'': 'lib'},
	packages=find_packages('lib'),
	package_data={
		'': ['data/*'],
	},
	classifiers=(
		b'Development Status :: 5 - Production/Stable',
		b'Environment :: Console',
		b'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		b'Operating System :: OS Independent',
		b'Programming Language :: Python :: 2.7',
		b'Programming Language :: Python :: 3.4',
		b'Programming Language :: Python :: 3.5',
		b'Topic :: Security'
	),
	scripts=['termineter']
)
