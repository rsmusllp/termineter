#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c1218/urlhandler/protocol_unix.py
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
import os
import socket
import time
import urlparse

from serial.serialutil import *
from serial.urlhandler.protocol_socket import SocketSerial

class UnixSerial(SocketSerial):
	"""
	Serial port implementation for unix sockets.
	"""
	def open(self):
		self.logger = None
		if self._port is None:
			raise SerialException('Port must be configured before it can be used.')
		if self._isOpen:
			raise SerialException('Port is already open.')
		try:
			self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			details = self.from_url(self.portstr)
			socket_path = details['path']
			if details['mode'] == 'server':
				if os.path.exists(socket_path):
					os.unlink(socket_path)
				self._socket.bind(socket_path)
				self._socket.listen(1)
				self._server_socket = self._socket
				self._socket = self._server_socket.accept()[0]
			else:
				self._socket.connect(socket_path)
		except Exception as error:
			self._socket = None
			raise SerialException("Could not open port {0}: {1}".format(self.portstr, repr(error)))
		self._socket.settimeout(2)
		self._isOpen = True

	def close(self):
		if not self._isOpen:
			return
		if self._socket:
			try:
				self._socket.shutdown(socket.SHUT_RDWR)
				self._socket.close()
			except:
				pass
			self._socket = None
		if hasattr(self, '_server_socket'):
			socket_file = self._server_socket.getsockname()
			try:
				self._server_socket.shutdown(socket.SHUT_RDWR)
				self._server_socket.close()
			except:
				pass
			delattr(self, '_server_socket')
			os.unlink(socket_file)
		self._isOpen = False

	def from_url(self, url):
		details = {}
		url = urlparse.urlparse(url)
		options = urlparse.parse_qs(url.query)
		options_get = lambda key, default: options.get(key, [default])[0]
		details['path'] = url.path
		details['mode'] = options_get('mode', 'client')
		assert(details['mode'] in ('server', 'client'))
		log_level = options_get('logging', 'ERROR').upper()
		assert(log_level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
		self.logger = logging.getLogger('c1218.connection.socket.unix')
		self.logger.setLevel(getattr(logging, log_level))
		return details

	def read(self, size=1):
		if not self._isOpen:
			raise portNotOpenError
		data = bytearray()
		if self._timeout != None:
			timeout = time.time() + self._timeout
		else:
			timeout = float('inf')
		while len(data) < size and time.time() < timeout:
			try:
				data = self._socket.recv(size - len(data))
			except socket.timeout:
				continue
			except socket.error as error:
				raise SerialException('connection failed (' + str(error) + ')')
		return bytes(data)

# assemble Serial class with the platform specific implementation and the base
# for file-like behavior. for Python 2.6 and newer, that provide the new I/O
# library, derive from io.RawIOBase
try:
	import io
except ImportError:
	# classic version with our own file-like emulation
	class Serial(UnixSerial, FileLike):
		pass
else:
	# io library present
	class Serial(UnixSerial, io.RawIOBase):
		pass
