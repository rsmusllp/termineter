#  c1219/errors.py
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

class C1219ProcedureError(Exception):
	"""
	Raised when a procedure can not be executed.
	"""
	def __init__(self, msg):
		self.message = msg

	def __str__(self):
		return repr(self.message)

class C1219ParseError(Exception):
	"""
	Raised when there is an error parsing data.

	:param int tableid: If the data originated from a table, the faulty table can be specified here.
	"""
	def __init__(self, msg, tableid=None):
		self.message = msg
		self.tableid = tableid

	def __str__(self):
		return repr(self.message)
