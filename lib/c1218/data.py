#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c1218/data.py
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

from c1218.utilities import check_data_checksum, data_checksum, packet_checksum

ACK = b'\x06'
NACK = b'\x15'

C1218_RESPONSE_CODES = {
	0: 'ok (Acknowledge)',
	1: 'err (Error)',
	2: 'sns (Service Not Supported)',
	3: 'isc (Insufficient Security Clearance)',
	4: 'onp (Operation Not Possible)',
	5: 'iar (Inappropriate Action Requested)',
	6: 'bsy (Device Busy)',
	7: 'dnr (Data Not Ready)',
	8: 'dlk (Data Locked)',
	9: 'rno (Renegotiate Request)',
	10: 'isss (Invalid Service Sequence State)',

	'ok':   0,
	'err':  1,
	'sns':  2,
	'isc':  3,
	'onp':  4,
	'iar':  5,
	'bsy':  6,
	'dnr':  7,
	'dlk':  8,
	'rno':  9,
	'isss': 10,
}

class C1218Request(object):
	def __repr__(self):
		return '<' + self.__class__.__name__ + ' >'

	def __str__(self):
		return self.build()

	def __len__(self):
		return len(self.build())

	def build(self):
		raise NotImplementedError('no build method defined')

	@classmethod
	def from_bytes(cls, data):
		raise NotImplementedError('no parse method defined')

	@classmethod
	def from_hex(cls, data):
		return cls.from_bytes(binascii.a2b_hex(data))

	@property
	def name(self):
		name = self.__class__.__name__
		if not name.startswith('C1218'):
			raise Exception('class name does not start with \'C1218\'')
		if not name.endswith('Request'):
			raise Exception('class name does not end with \'Request\'')
		return name[5:-7]

class C1218LogonRequest(C1218Request):
	logon = b'\x50'
	def __init__(self, username='', userid=0):
		self._userid = b'\x00\x00'
		self._username = b'\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20'
		self.set_username(username)
		self.set_userid(userid)

	def build(self):
		return self.logon + self._userid + self._username

	@classmethod
	def from_bytes(cls, data):
		if len(data) != 13:
			raise Exception('invalid data (size)')
		if data[0] != 0x50:
			raise Exception('invalid start byte')
		userid = struct.unpack('>H', data[1:3])[0]
		username = data[3:]
		return cls(username, userid)

	def set_userid(self, userid):
		if isinstance(userid, str) and userid.isdigit():
			userid = int(userid)
		elif not isinstance(userid, int):
			ValueError('userid must be between 0x0000 and 0xffff')
		if not 0x0000 <= userid <= 0xffff:
			raise ValueError('userid must be between 0x0000 and 0xffff')
		self._userid = struct.pack('>H', userid)

	@property
	def userid(self):
		return struct.unpack('>H', self._userid)[0]

	def set_username(self, value):
		if len(value) > 10:
			raise ValueError('username must be 10 characters or less')
		if not isinstance(value, bytes):
			value = value.encode('utf-8')
		self._username = value + (b'\x20' * (10 - len(value)))

	@property
	def username(self):
		return self._username

class C1218SecurityRequest(C1218Request):
	security = b'\x51'
	def __init__(self, password=''):
		self._password = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
		self.set_password(password)

	def build(self):
		return self.security + self._password

	@classmethod
	def from_bytes(cls, data):
		if len(data) != 21:
			raise Exception('invalid data (size)')
		if data[0] != 0x51:
			raise Exception('invalid start byte')
		password = data[1:21]
		return cls(password)

	def set_password(self, value):
		if len(value) > 20:
			raise ValueError('password must be 20 byte or less')
		if not isinstance(value, bytes):
			value = value.encode('utf-8')
		self._password = value + (b'\x00' * (20 - len(value)))

	@property
	def password(self):
		return self._password

class C1218LogoffRequest(C1218Request):
	logoff = b'\x52'
	def build(self):
		return self.logoff

	@classmethod
	def from_bytes(cls, data):
		if len(data) != 1:
			raise Exception('invalid data (size)')
		if data[0] != 0x52:
			raise Exception('invalid start byte')
		return cls()

class C1218NegotiateRequest(C1218Request):
	negotiate = b'\x60'
	def __init__(self, pktsize, nbrpkt, baudrate=None):
		self._pktsize = b'\x01\x00'
		self._nbrpkt = 1
		self._baudrate = b''
		self.set_pktsize(pktsize)
		self.set_nbrpkt(nbrpkt)
		if baudrate:
			self.set_baudrate(baudrate)

	def build(self):
		pktsize = struct.pack('>H', self._pktsize)
		nbrpkt = struct.pack('B', self._nbrpkt)
		return self.negotiate + pktsize + nbrpkt + self._baudrate

	@classmethod
	def from_bytes(cls, data):
		if data[0] == 0x60:
			baud_included = False
			if len(data) != 4:
				raise Exception('invalid data (size)')
		elif data[0] < 0x6c and data[0] > 0x60:
			baud_included = True
			if len(data) != 5:
				raise Exception('invalid data (size)')
		else:
			raise Exception('invalid start byte')
		pktsize = struct.unpack('>H', data[1:3])[0]
		nbrpkt = data[3]
		baudrate = None
		if baud_included:
			baudrate = data[4]
			if baudrate == 0 or baudrate > 10:
				raise Exception('invalid data (invalid baudrate)')
		request = cls(pktsize, nbrpkt, baudrate)
		request.negotiate = struct.pack('B', data[0])
		return request

	def set_pktsize(self, pktsize):
		self._pktsize = pktsize

	def set_nbrpkt(self, nbrpkt):
		self._nbrpkt = nbrpkt

	def set_baudrate(self, baudrate):
		c1218_baudrate_codes = {300: 1, 600: 2, 1200: 3, 2400: 4, 4800: 5, 9600: 6, 14400: 7, 19200: 8, 28800: 9, 57600: 10}
		if baudrate in c1218_baudrate_codes:
			self._baudrate = struct.pack('B', c1218_baudrate_codes[baudrate])
		elif 0 < baudrate < 11:
			self._baudrate = struct.pack('B', baudrate)
		else:
			raise Exception('invalid data (invalid baudrate)')
		self.negotiate = b'\x61'

class C1218WaitRequest(C1218Request):
	wait = b'\x70'
	def __init__(self, time=1):
		self._time = b'\x01'
		self.set_time(time)

	def build(self):
		return self.wait + self._time

	@classmethod
	def from_bytes(cls, data):
		if len(data) != 2:
			raise Exception('invalid data (size)')
		if data[0] != 0x70:
			raise Exception('invalid start byte')
		return cls(data[1])

	def set_time(self, time):
		self._time = struct.pack('B', time)

class C1218IdentRequest(C1218Request):
	ident = b'\x20'
	def build(self):
		return self.ident

	@classmethod
	def from_bytes(cls, data):
		if len(data) != 1:
			raise Exception('invalid data (size)')
		if data[0] != 0x20:
			raise Exception('invalid start byte')
		return cls()

class C1218TerminateRequest(C1218Request):
	terminate = b'\x21'
	def build(self):
		return self.terminate

	@classmethod
	def from_bytes(cls, data):
		if len(data) != 1:
			raise Exception('invalid data (size)')
		if data[0] != 0x21:
			raise Exception('invalid start byte')
		return cls()

class C1218ReadRequest(C1218Request):
	read = b'\x30'
	def __init__(self, tableid, offset=None, octetcount=None):
		self._tableid = b'\x00\x01'
		self._offset = b''
		self._octetcount = b''
		self.set_tableid(tableid)
		if offset is not None or octetcount is not None:
			self.read = b'\x3f'
			self.set_offset(offset or 0)
			self.set_octetcount(octetcount or 0)

	def build(self):
		return self.read + self._tableid + self._offset + self._octetcount

	@classmethod
	def from_bytes(cls, data):
		if (data[0] == 0x30 and len(data) < 3) or (data[0] == 0x3f and len(data) < 8):
			raise Exception('invalid data (size)')
		if data[0] != 0x30 and data[0] != 0x3f:
			raise Exception('invalid start byte')
		tableid = struct.unpack('>H', data[1:3])[0]
		if data[0] == 0x30:
			offset = None
			octetcount = None
		elif data[0] == 0x3f:
			offset = struct.unpack('>I', b'\x00' + data[3:6])[0]
			octetcount = struct.unpack('>H', data[6:8])[0]
		request = cls(tableid, offset, octetcount)
		request.read = struct.pack('B', data[0])
		return request

	def set_tableid(self, tableid):
		self._tableid = struct.pack('>H', tableid)

	@property
	def tableid(self):
		return struct.unpack('>H', self._tableid)[0]

	def set_offset(self, offset):
		if self._octetcount and self._offset:
			self.read = b'\x3f'
		self._offset = struct.pack('>I', (offset & 0xffffff))[1:]

	@property
	def offset(self):
		if self._offset == b'':
			return None
		return struct.unpack('>I', b'\x00' + self._offset)[0]

	def set_octetcount(self, octetcount):
		if self._octetcount and self._offset:
			self.read = b'\x3f'
		self._octetcount = struct.pack('>H', octetcount)

	@property
	def octetcount(self):
		if self._octetcount == b'':
			return None
		return struct.unpack('>H', self._octetcount)[0]

class C1218WriteRequest(C1218Request):
	write = b'\x40'
	def __init__(self, tableid, data, offset=None):
		self._tableid = b'\x00\x01'
		self._offset = b''
		self._datalen = b'\x00\x00'
		self._data = b''
		self._crc8 = b''
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

	@classmethod
	def from_bytes(cls, data):
		if len(data) < 3:
			raise Exception('invalid data (size)')
		if data[0] != 0x40 and data[0] != 0x4f:
			raise Exception('invalid start byte')
		tableid = struct.unpack('>H', data[1:3])[0]
		chksum = data[-1]
		if data[0] == 0x40:
			table_data = data[5:-1]
			offset = None
		elif data[0] == 0x4f:
			table_data = data[8:-1]
			offset = struct.unpack('>I', b'\x00' + data[3:6])[0]
		if check_data_checksum(table_data, chksum):
			raise Exception('invalid check sum')
		request = cls(tableid, table_data, offset=offset)
		request.write = data[0]
		return request

	def set_tableid(self, tableid):
		self._tableid = struct.pack('>H', tableid)

	@property
	def tableid(self):
		return struct.unpack('>H', self._tableid)[0]

	def set_offset(self, offset):
		self._offset = struct.pack('>I', (offset & 0xffffff))[1:]

	@property
	def offset(self):
		if self._offset == b'':
			return None
		return struct.unpack('>I', b'\x00' + self._offset)[0]

	def set_data(self, data):
		self._data = data
		self._datalen = struct.pack('>H', len(data))

	@property
	def data(self):
		return self._data

class C1218Packet(C1218Request):
	start = b'\xee'
	identity = b'\x00'
	control = b'\x00'
	sequence = b'\x00'
	def __init__(self, data=None, control=None, length=None):
		self._length = b'\x00\x00'  # can never exceed 8183
		self._data = b''
		if data:
			self.set_data(data)
		if length:
			self.set_length(length)
		if control:
			self.set_control(control)

	def __repr__(self):
		if isinstance(self._data, C1218Request):
			repr_data = repr(self._data)
		else:
			repr_data = '0x' + binascii.b2a_hex(self._data).decode('utf-8')
		crc = binascii.b2a_hex(packet_checksum(self.start + self.identity + self.control + self.sequence + self._length + self._data)).decode('utf-8')
		return '<C1218Packet data=' + repr_data + ' data_len=' + str(len(self._data)) + ' crc=0x' + crc + ' >'

	@property
	def data(self):
		return self._data

	@data.setter
	def data(self, value):
		self.set_data(value)

	@classmethod
	def from_bytes(cls, data):
		if len(data) < 8:
			raise Exception('invalid data (size)')
		if data[0] != 0xee:
			raise Exception('invalid start byte')
		identity = data[1]
		control = data[2]
		sequence = data[3]
		length = struct.unpack('>H', data[4:6])[0]
		chksum = data[-2:]
		if packet_checksum(data[:-2]) != chksum:
			raise Exception('invalid check sum')
		data = data[6:-2]
		frame = C1218Packet(data, control, length)
		frame.identity = struct.pack('B', identity)
		frame.sequence = struct.pack('B', sequence)
		return frame

	def set_control(self, control):
		if isinstance(control, int):
			if not (0x00 < control < 0xff):
				raise ValueError('control must be between 0x00 and 0xff')
			control = struct.pack('B', control)
		if not isinstance(control, bytes):
			raise ValueError('control must be an int or bytes instance')
		self.control = control

	def set_data(self, data):
		if isinstance(data, C1218Request):
			data = data.build()
		elif not isinstance(data, bytes):
			data = data.encode('utf-8')
		self._data = data
		self.set_length(len(self._data))

	def set_length(self, length):
		if length > 8183:
			raise ValueError('length can not exceed 8183')
		self._length = struct.pack('>H', length)

	def build(self):
		packet = self.start
		packet += self.identity
		packet += self.control
		packet += self.sequence
		packet += self._length
		packet += self._data
		packet += packet_checksum(packet)
		return packet

C1218_REQUEST_IDS = {
	0x20: C1218IdentRequest,
	0x21: C1218TerminateRequest,
	0x30: C1218ReadRequest,
	0x3f: C1218ReadRequest,
	0x40: C1218WriteRequest,
	0x4f: C1218WriteRequest,
	0x50: C1218LogonRequest,
	0x51: C1218SecurityRequest,
	0x52: C1218LogoffRequest,
	0x60: C1218NegotiateRequest,
	0x61: C1218NegotiateRequest,
	0x70: C1218WaitRequest,
}
