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

class C1218IOError(Exception):
	"""
	Raised when there is a problem sending or receiving data.
	"""
	def __init__(self, msg):
		self.message = msg
		
	def __str__(self):
		return repr(self.message)

class C1218ReadTableError(Exception):
	"""
	Raised when a table is not successfully read.
	
	@type errcode: Integer
	@param errcode: The error that was returned while reading the table.
	"""
	def __init__(self, msg, errcode = None):
		self.message = msg
		self.errCode = errcode
	
	def __str__(self):
		return repr(self.message)

class C1218WriteTableError(Exception):
	"""
	Raised when a table is not successfully written to.
	
	@type errcode: Integer
	@param errcode: The error that was returned while writing to the table.
	"""
	def __init__(self, msg, errcode = None):
		self.message = msg
		self.errCode = errcode
	
	def __str__(self):
		return repr(self.message)
