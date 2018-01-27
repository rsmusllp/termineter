#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c1222/data.py
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

import binascii
import struct

from c1222.utilities import data_checksum

from pyasn1.codec.ber import encoder as ber_encoder
from pyasn1.codec.ber import decoder as ber_decoder
from pyasn1.type import tag
from pyasn1.type import univ

class C1222CallingAPTitle(univ.ObjectIdentifier):
	tagSet = univ.ObjectIdentifier.tagSet.tagExplicitly(tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 6))

	def encode(self):
		return ber_encoder.encode(self)

class C1222CallingAPInvocationID(univ.Integer):
	tagSet = univ.Integer.tagSet.tagExplicitly(tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 8))

	def encode(self):
		return ber_encoder.encode(self)

class C1222CalledAPTitle(univ.ObjectIdentifier):
	tagSet = univ.ObjectIdentifier.tagSet.tagExplicitly(tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 2))

	def encode(self):
		return ber_encoder.encode(self)

class C1222Data(object):
	"""
	This class provides basic methods for constructable data fragments of the
	C12.22 protocol.
	"""
	def __repr__(self):
		return '<' + self.__class__.__name__ + ' >'

	def __str__(self):
		return self.build()

	def __len__(self):
		return len(self.build())

	def build(self):
		return b''

class C1222EPSEM(C1222Data):
	def __init__(self, data, ed_class=b''):
		self.data = data
		# flags
		self.reserved = False
		self.recovery = False
		self.proxy_service = False
		self.ed_class = ed_class
		self.security_mode = 0
		self.response_mode = 0

	def __repr__(self):
		return '<C1222EPSEM data=0x' + binascii.b2a_hex(self.data).decode('utf-8') + ' data_len=' + str(len(self.data)) + ' >'

	@classmethod
	def from_bytes(cls, data):
		if len(data) < 2:
			raise Exception('invalid data (size)')
		flags = data[0]

		reserved = bool(flags & (1 << 7))
		recovery = bool(flags & (1 << 6))
		proxy_service = bool(flags & (1 << 5))
		ed_class = bool(flags & (1 << 4))
		security_mode = ((flags & (3 << 2)) >> 2)
		response_mode = (flags & 3)
		if ed_class:
			ed_class = data[1:5]
			length = data[5]
			data = data[6:]
		else:
			ed_class = b''
			length = data[1]
			data = data[2:]
		if length != len(data):
			raise Exception('invalid data (size)')
		epsem = cls(data, ed_class)
		epsem.reserved = reserved
		epsem.recovery = recovery
		epsem.proxy_service = proxy_service
		epsem.security_mode = security_mode
		epsem.response_mode = response_mode
		return epsem

	def build(self):
		flags = 0
		flags |= (int(self.reserved) << 7)
		flags |= (int(self.recovery) << 6)
		flags |= (int(self.proxy_service) << 5)
		flags |= (int(bool(self.ed_class)) << 4)
		flags |= (self.security_mode << 2)
		flags |= self.response_mode
		flags = struct.pack('B', flags)
		data = str(self.data)
		return flags + self.ed_class + struct.pack('B', len(data)) + data

class C1222UserInformation(C1222Data):
	def __init__(self, data):
		self.data = data

	@classmethod
	def from_bytes(cls, data):
		if len(data) < 6:
			raise Exception('invalid data (size)')
		if data[0] != 0xbe:
			raise Exception('invalid start byte')
		if data[1] != len(data[2:]):
			raise Exception('invalid data (size)')

		if data[2] != 0x28:
			raise Exception('invalid start byte')
		if ord(data[3]) != len(data[4:]):
			raise Exception('invalid data (size)')

		if data[4] != 0x81:
			raise Exception('invalid start byte')
		if data[5] != len(data[6:]):
			raise Exception('invalid data (size)')
		return cls(data[6:])

	def build(self):
		data = self.data
		data = b'\x81' + struct.pack('B', len(data)) + data
		data = b'\x28' + struct.pack('B', len(data)) + data
		data = b'\xbe' + struct.pack('B', len(data)) + data
		return data

class C1222Request(C1222Data):
	@property
	def name(self):
		name = self.__class__.__name__
		if not name.startswith('C1222'):
			raise Exception('class name does not start with \'C1222\'')
		if not name.endswith('Request'):
			raise Exception('class name does not end with \'Request\'')
		return name[5:-7]

	def set_ap_title(self, ap_title):
		if not hasattr(self, '_ap_title'):
			raise Exception(self.__class__.__name__ + ' does not support the ap_title element')
		if isinstance(ap_title, univ.ObjectIdentifier):
			self._ap_title = ber_encoder.encode(ap_title)
		if isinstance(ap_title, str):
			self._ap_title = ap_title
		else:
			self._ap_title = ber_encoder.encode(univ.ObjectIdentifier(ap_title))

	def set_userid(self, userid):
		if not hasattr(self, '_userid'):
			raise Exception(self.__class__.__name__ + ' does not support the userid element')
		if not isinstance(userid, int):
			ValueError('userid must be between 0x0000 and 0xffff')
		if not 0x0000 <= userid <= 0xffff:
			raise ValueError('userid must be between 0x0000 and 0xffff')
		self._userid = struct.pack('>H', userid)

class C1222DisconnectRequest(C1222Request):
	disconnect = b'\x22'

	def build(self):
		return self.disconnect

class C1222IdentRequest(C1222Request):
	ident = b'\x20'

	def build(self):
		return self.ident

class C1222LogoffRequest(C1222Request):
	logoff = b'\x52'

	def build(self):
		return self.logoff

class C1222LogonRequest(C1222Request):
	logon = b'\x50'
	def __init__(self, username='', userid=0, session_idle_timeout=0):
		self._userid = b'\x00\x00'
		self._username = b'\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20'
		self._session_idle_timeout = b'\x00\x00'
		self.set_username(username)
		self.set_userid(userid)
		self.set_session_idle_timeout(session_idle_timeout)

	def build(self):
		return self.logon + self._userid + self._username + self._session_idle_timeout

	def set_username(self, value):
		if len(value) > 10:
			raise ValueError('username must be 10 characters or less')
		self._username = value.encode('utf-8') + (b'\x20' * (10 - len(value)))

	def set_session_idle_timeout(self, session_idle_timeout):
		if not isinstance(session_idle_timeout, int):
			ValueError('session_idle_timeout must be between 0x0000 and 0xffff')
		if not 0x0000 <= session_idle_timeout <= 0xffff:
			raise ValueError('session_idle_timeout must be between 0x0000 and 0xffff')
		self._session_idle_timeout = struct.pack('>H', session_idle_timeout)

class C1222ReadRequest(C1222Request):
	read = b'\x30'
	def __init__(self, tableid, offset=None, octetcount=None):
		self._tableid = b'\x00\x01'
		self._offset = b''
		self._octetcount = b''
		self.set_tableid(tableid)
		if (offset is not None and offset != 0) and (octetcount is not None and octetcount != 0):
			self.read = b'\x3f'
			self.set_offset(offset)
			self.set_octetcount(octetcount)

	def build(self):
		return self.read + self._tableid + self._offset + self._octetcount

	def set_tableid(self, tableid):
		self._tableid = struct.pack('>H', tableid)

	def set_offset(self, offset):
		self._offset = struct.pack('>I', (offset & 0xffffff))[1:]

	def set_octetcount(self, octetcount):
		self._octetcount = struct.pack('>H', octetcount)

class C1222ResolveRequest(C1222Request):
	resolve = b'\x25'
	def __init__(self, ap_title):
		self._ap_title = b''
		self.set_ap_title(ap_title)

	def build(self):
		return self.resolve + self._ap_title

class C1222SecurityRequest(C1222Request):
	security = b'\x51'
	def __init__(self, password='', userid=0):
		self._password = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
		self._userid = b'\x00\x00'
		self.set_password(password)
		self.set_userid(userid)

	def build(self):
		return self.security + self._password + self._userid

	def set_password(self, value):
		if len(value) > 20:
			raise ValueError('password must be 20 characters or less')
		self._password = value.encode('utf-8') + (b'\x20' * (20 - len(value)))

class C1222TerminateRequest(C1222Request):
	terminate = b'\x21'

	def build(self):
		return self.terminate

class C1222TraceRequest(C1222Request):
	trace = b'\x26'
	def __init__(self, ap_title):
		self._ap_title = b''
		self.set_ap_title(ap_title)

	def build(self):
		return self.trace + self._ap_title

class C1222WaitRequest(C1222Request):
	wait = b'\x70'
	def __init__(self, time=0):
		self._time = b'\x00'
		self.set_time(time)

	def build(self):
		return self.wait + self._time

	def set_time(self, time):
		self._time = struct.pack('B', time)

class C1222WriteRequest(C1222Request):
	write = b'\x40'
	def __init__(self, tableid, data, offset=None):
		self._tableid = b'\x00\x01'
		self._offset = b''
		self._datalen = b'\x00\x00'
		self._data = b''
		self.set_tableid(tableid)
		self.set_data(data)
		if offset is not None and offset != 0:
			self.write = b'\x4f'
			self.set_offset(offset)

	def build(self):
		packet = self.write
		packet += self._tableid
		packet += self._offset
		packet += self._datalen
		packet += self._data
		packet += data_checksum(self._data)
		return packet

	def set_tableid(self, tableid):
		self._tableid = struct.pack('>H', tableid)

	def set_offset(self, offset):
		self._offset = struct.pack('>I', (offset & 0xffffff))[1:]

	def set_data(self, data):
		self._data = data
		self._datalen = struct.pack('>H', len(data))

class C1222Packet(C1222Request):
	start = b'\x60'
	def __init__(self, called_ap, calling_ap, calling_ap_invocation_id, data=None, length=None):
		self._length = b'\x00'
		self._data = b''
		if not isinstance(called_ap, C1222CalledAPTitle):
			called_ap = C1222CalledAPTitle(called_ap)
		self.called_ap = called_ap

		if not isinstance(calling_ap, C1222CallingAPTitle):
			calling_ap = C1222CallingAPTitle(calling_ap)
		self.calling_ap = calling_ap

		if not isinstance(calling_ap_invocation_id, C1222CallingAPInvocationID):
			calling_ap_invocation_id = C1222CallingAPInvocationID(calling_ap_invocation_id)
		self.calling_ap_invocation_id = calling_ap_invocation_id

		if data:
			self.set_data(data)
		else:
			self.set_data(b'')
		if length:
			self.set_length(length)

	def __repr__(self):
		if isinstance(self._data, C1222Data):
			return '<C1222Packet data=' + repr(self._data) + ' data_len=' + str(len(self._data)) + ' >'
		else:
			return '<C1222Packet data=0x' + str(self._data).encode('hex') + ' data_len=' + str(len(self._data)) + ' >'

	@classmethod
	def from_bytes(cls, data):
		if data[0] != 0x60:
			raise Exception('invalid start byte')

		(called_ap, data) = ber_decoder.decode(data)
		(called_ap_invocation_id, data) = ber_decoder.decode(data)
		(calling_ap, data) = ber_decoder.decode(data)
		(calling_ap_invocation_id, data) = ber_decoder.decode(data)

		if data[0] == 0xbe:
			data = C1222UserInformation.from_bytes(data)

		called_ap = C1222CalledAPTitle(called_ap)
		calling_ap = C1222CallingAPTitle(calling_ap)
		calling_ap_invocation_id = C1222CallingAPInvocationID(calling_ap_invocation_id)

		frame = cls(called_ap, calling_ap, calling_ap_invocation_id, data)
		return frame

	@property
	def data(self):
		return self._data

	@data.setter
	def data(self, value):
		self.set_data(value)

	def set_data(self, value):
		self._data = value
		length = len(self.called_ap.encode())
		length += len(self.calling_ap.encode())
		length += len(self.calling_ap_invocation_id.encode())
		length += len(self._data)
		self.set_length(length)

	def set_length(self, length):
		self._length = struct.pack('B', length)

	def build(self):
		packet = self.start
		packet += self._length
		packet += self.called_ap.encode()
		packet += self.calling_ap.encode()
		packet += self.calling_ap_invocation_id.encode()
		packet += self._data
		return packet
