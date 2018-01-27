#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/utilities.py
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

from __future__ import unicode_literals

import copy
import itertools

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
