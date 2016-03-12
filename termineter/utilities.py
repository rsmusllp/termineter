#  termineter/utilities.py
#
#  Copyright 2012 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
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

from __future__ import unicode_literals

import copy
import itertools
import os

import serial

DEFAULT_SERIAL_SETTINGS = {
	'parity': serial.PARITY_NONE,
	'baudrate': 9600,
	'bytesize': serial.EIGHTBITS,
	'xonxoff': False,
	'interCharTimeout': None,
	'rtscts': False,
	'timeout': 1,
	'stopbits': serial.STOPBITS_ONE,
	'dsrdtr': False,
	'writeTimeout': None
}

def get_default_serial_settings():
	return copy.copy(DEFAULT_SERIAL_SETTINGS)

class Namespace:
	"""
	This class is used to hold attributes of the framework.  It doesn't
	really do anything, it's used for organizational purposes only.
	"""
	pass

def unique(seq, idfunc=None):
	"""
	Unique a list or tuple and preserve the order

	@type idfunc: Function or None
	@param idfunc: If idfunc is provided it will be called during the
	comparison process.
	"""
	if idfunc is None:
		idfunc = lambda x: x
	preserved_type = type(seq)
	seen = {}
	result = []
	for item in seq:
		marker = idfunc(item)
		if marker in seen:
			continue
		seen[marker] = 1
		result.append(item)
	return preserved_type(result)

class StringGenerator:
	def __init__(self, startlen, endlen=None, charset=None):
		"""
		This class is used to generate raw strings for bruteforcing.

		@type startlen: Integer
		@param startlen: The minimum size of the string to bruteforce.

		@type endlen: Integer
		@param endlen: The maximum size of the string to bruteforce.

		@type charset: String, Tuple or None
		@param charset: the character set to use while generating the
		strings.  If None, the full binary space will be used (0 - 255).
		"""
		self.startlen = startlen
		if endlen is None:
			self.endlen = startlen
		else:
			self.endlen = endlen
		if charset is None:
			charset = map(chr, range(0, 256))
		elif type(charset) == str:
			charset = list(charset)
		charset = unique(charset)
		charset.sort()
		self.charset = tuple(charset)

	def __iter__(self):
		length = self.startlen
		while length <= self.endlen:
			for string in itertools.product(self.charset, repeat=length):
				yield ''.join(string)
			length += 1
		raise StopIteration
