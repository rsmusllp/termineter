#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c1218/errors.py
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

class C1218Error(Exception):
	"""
	This is a generic C1218 Error.
	"""
	def __init__(self, msg, code=None):
		self.message = msg
		self.code = code

	def __str__(self):
		return repr(self.message)

class C1218IOError(C1218Error):
	"""
	Raised when there is a problem sending or receiving data.
	"""
	def __init__(self, msg):
		self.message = msg

class C1218NegotiateError(C1218Error):
	"""
	Raised in response to an invalid reply to a Negotiate request.
	"""
	pass

class C1218ReadTableError(C1218Error):
	"""
	Raised when a table is not successfully read.

	:param int errcode: The error that was returned while reading the table.
	"""
	pass

class C1218WriteTableError(C1218Error):
	"""
	Raised when a table is not successfully written to.

	:param int errcode: The error that was returned while writing to the table.
	"""
	pass
