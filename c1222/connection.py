#  c1222/connection.py
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

from binascii import hexlify, unhexlify
from struct import pack, unpack
import logging
import socket
from c1222.data import *

class Connection:
	def __init__(self, host, called_ap, calling_ap, enable_cache = True):
		self.logger = logging.getLogger('c1222.connection')
		self.loggerio = logging.getLogger('c1222.connection.io')
		self.host = host
		self.sock_h = socket.create_connection(host)
		self.logger.debug('successfully connected to: ' + host[0] + ':' + str(host[1]))
		
		if not isinstance(called_ap, C1222CalledAPTitle):
			called_ap = C1222CalledAPTitle(called_ap)
		self.called_ap = called_ap
		
		if not isinstance(calling_ap, C1222CallingAPTitle):
			calling_ap = C1222CallingAPTitle(calling_ap)
		self.calling_ap = calling_ap
		
		self.logged_in = False
		self.__initialized__ = False
		self.c1219_endian = '<'
		self.caching_enabled = enable_cache
		self.__cacheable_tbls__ = [0, 1]
		self.__tbl_cache__ = {}
		if enable_cache:
			self.logger.info('selective table caching has been enabled')
