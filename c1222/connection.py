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

from __future__ import unicode_literals

import logging
import random
import select
import socket

from c1222.data import *
from c1222.errors import C1222IOError

if hasattr(logging, 'NullHandler'):
	logging.getLogger('c1222').addHandler(logging.NullHandler())

def sock_read_ready(socket, timeout):
	readys = select.select([socket.fileno()], [], [], timeout)
	return len(readys[0]) == 1

class Connection:
	def __init__(self, host, called_ap, calling_ap, enable_cache=True, bind_host=('', 1153)):
		self.logger = logging.getLogger('c1222.connection')
		self.loggerio = logging.getLogger('c1222.connection.io')

		self.read_timeout = 3.0
		self.server_sock_h = None
		self.read_sock_h = None
		self.bind_host = bind_host
		self.start_listener()

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

	def start_listener(self):
		if self.server_sock_h is not None:
			raise Exception('server socket already created')
		self.server_sock_h = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_sock_h.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_sock_h.bind(self.bind_host)
		self.server_sock_h.listen(1)

	def stop_listener(self):
		if self.server_sock_h is None:
			return
		self.server_sock_h.close()
		self.server_sock_h = None

	def recv(self):
		if self.read_sock_h is None:
			readable = select.select([self.sock_h.fileno(), self.server_sock_h.fileno()], [], [], self.read_timeout)
			readable = readable[0]
			if len(readable) > 1:
				raise C1222IOError('too many file handles available for reading')
			if len(readable) < 1:
				raise C1222IOError('not enough file handles available for reading')
			readable = readable[0]
			if readable == self.server_sock_h.fileno():
				(self.read_sock_h, addr) = self.server_sock_h.accept()
				self.logger.info("received connection from {0}:{1}".format(addr[0], addr[1]))
				self.stop_listener()
			elif readable == self.sock_h.fileno():
				self.read_sock_h = self.sock_h
				self.stop_listener()
			else:
				raise C1222IOError('unknown file handle is available for reading')
		data = b''
		while sock_read_ready(self.read_sock_h, self.read_timeout):
			tmp_data = self.read_sock_h.recv(8192)
			data += tmp_data
			if len(tmp_data) != 8192:
				break
		pkt = C1222Packet.parse(data)
		if not isinstance(pkt.data, C1222UserInformation):
			return pkt.data
		return C1222EPSEM.parse(pkt.data.data)

	def send(self, data):
		pkt = C1222Packet(self.called_ap, self.calling_ap, random.randint(0, 999999), data=C1222UserInformation(C1222EPSEM(data)))
		self.sock_h.send(pkt.build())

	def start(self):
		self.send(C1222IdentRequest())
		try:
			self.recv()
		except C1222IOError:
			self.logger.error('received incorrect response to identification service request')
		else:
			return True
		return False

	def close(self):
		self.sock_h.close()
		if self.read_sock_h is not None:
			self.read_sock_h.close()
		self.stop_listener()
