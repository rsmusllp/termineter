#  c1218/errors.py
#
#  Copyright 2011 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
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
