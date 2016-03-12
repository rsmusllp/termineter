#  c1222/errors.py
#
#  Copyright 2013 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
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

class C1222Error(Exception):
	"""
	This is a generic C1222 Error.
	"""
	def __init__(self, msg, error_code=None):
		self.message = msg
		self.err_code = error_code

	def __str__(self):
		return repr(self.message)

class C1222IOError(C1222Error):
	"""
	Raised when there is a problem sending or receiving data.
	"""
	def __init__(self, msg):
		self.message = msg

class C1222NegotiateError(C1222Error):
	"""
	Raised in response to an invalid reply to a Negotiate request.
	"""
	pass

class C1222ReadTableError(C1222Error):
	"""
	Raised when a table is not successfully read.

	@type errcode: Integer
	@param errcode: The error that was returned while reading the table.
	"""
	pass

class C1222WriteTableError(C1222Error):
	"""
	Raised when a table is not successfully written to.

	@type errcode: Integer
	@param errcode: The error that was returned while writing to the table.
	"""
	pass
