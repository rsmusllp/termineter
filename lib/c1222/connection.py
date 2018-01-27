#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c1222/connection.py
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

class Connection(object):
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
		self._initialized = False
		self.c1219_endian = '<'
		self.caching_enabled = enable_cache
		self._cacheable_tables = [0, 1]
		self._table_cache = {}
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
		pkt = C1222Packet.from_bytes(data)
		if not isinstance(pkt.data, C1222UserInformation):
			return pkt.data
		return C1222EPSEM.from_bytes(pkt.data.data)

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
