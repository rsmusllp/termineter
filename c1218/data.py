#  c1218/data.py
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

	@staticmethod
	def parse(data):
		raise NotImplementedError('no parse method defined')

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
	__userid__ = b'\x00\x00'
	__username__ = b'\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20'

	def __init__(self, username='', userid=0):
		self.set_username(username)
		self.set_userid(userid)

	def build(self):
		return self.logon + self.__userid__ + self.__username__

	@staticmethod
	def parse(data):
		if len(data) != 13:
			raise Exception('invalid data (size)')
		if data[0] != b'\x50':
			raise Exception('invalid start byte')
		userid = struct.unpack('>H', data[1:3])[0]
		username = data[3:]
		return C1218LogonRequest(username, userid)

	def set_userid(self, userid):
		if isinstance(userid, str) and userid.isdigit():
			userid = int(userid)
		elif not isinstance(userid, int):
			ValueError('userid must be between 0x0000 and 0xffff')
		if not 0x0000 <= userid <= 0xffff:
			raise ValueError('userid must be between 0x0000 and 0xffff')
		self.__userid__ = struct.pack('>H', userid)

	@property
	def userid(self):
		return struct.unpack('>H', self.__userid__)[0]

	def set_username(self, value):
		if len(value) > 10:
			raise ValueError('username must be 10 characters or less')
		if not isinstance(value, bytes):
			value = value.encode('utf-8')
		self.__username__ = value + (b'\x20' * (10 - len(value)))

	@property
	def username(self):
		return self.__username__

class C1218SecurityRequest(C1218Request):
	security = b'\x51'
	__password__ = b'\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20'

	def __init__(self, password=''):
		self.set_password(password)

	def build(self):
		return self.security + self.__password__

	@staticmethod
	def parse(data):
		if len(data) != 21:
			raise Exception('invalid data (size)')
		if data[0] != b'\x51':
			raise Exception('invalid start byte')
		password = data[1:21]
		return C1218SecurityRequest(password)

	def set_password(self, value):
		if len(value) > 20:
			raise ValueError('password must be 20 byte or less')
		if not isinstance(value, bytes):
			value = value.encode('utf-8')
		self.__password__ = value + (b'\x20' * (20 - len(value)))

	@property
	def password(self):
		return self.__password__

class C1218LogoffRequest(C1218Request):
	logoff = b'\x52'

	def build(self):
		return self.logoff

	@staticmethod
	def parse(data):
		if len(data) != 1:
			raise Exception('invalid data (size)')
		if data[0] != b'\x52':
			raise Exception('invalid start byte')
		return C1218LogoffRequest()

class C1218NegotiateRequest(C1218Request):
	negotiate = b'\x60'
	__pktsize__ = b'\x01\x00'
	__nbrpkt__ = 1
	__baudrate__ = b''

	def __init__(self, pktsize, nbrpkt, baudrate=None):
		self.set_pktsize(pktsize)
		self.set_nbrpkt(nbrpkt)
		if baudrate:
			self.set_baudrate(baudrate)

	def build(self):
		pktsize = struct.pack('>H', self.__pktsize__)
		nbrpkt = struct.pack('B', self.__nbrpkt__)
		return self.negotiate + pktsize + nbrpkt + self.__baudrate__

	@staticmethod
	def parse(data):
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
		request = C1218NegotiateRequest(pktsize, nbrpkt, baudrate)
		request.negotiate = data[0]
		return request

	def set_pktsize(self, pktsize):
		self.__pktsize__ = pktsize

	def set_nbrpkt(self, nbrpkt):
		self.__nbrpkt__ = nbrpkt

	def set_baudrate(self, baudrate):
		c1218_baudrate_codes = {300: 1, 600: 2, 1200: 3, 2400: 4, 4800: 5, 9600: 6, 14400: 7, 19200: 8, 28800: 9, 57600: 10}
		if baudrate in c1218_baudrate_codes:
			self.__baudrate__ = struct.pack('B', c1218_baudrate_codes[baudrate])
		elif 0 < baudrate < 11:
			self.__baudrate__ = struct.pack('B', baudrate)
		else:
			raise Exception('invalid data (invalid baudrate)')
		self.negotiate = b'\x61'

class C1218WaitRequest(C1218Request):
	wait = b'\x70'
	__time__ = b'\x01'

	def __init__(self, time=1):
		self.set_time(time)

	def build(self):
		return self.wait + self.__time__

	@staticmethod
	def parse(data):
		if len(data) != 2:
			raise Exception('invalid data (size)')
		if data[0] != b'\x70':
			raise Exception('invalid start byte')
		return C1218WaitRequest(ord(data[1]))

	def set_time(self, time):
		self.__time__ = chr(time)

class C1218IdentRequest(C1218Request):
	ident = b'\x20'

	def build(self):
		return self.ident

	@staticmethod
	def parse(data):
		if len(data) != 1:
			raise Exception('invalid data (size)')
		if data[0] != b'\x20':
			raise Exception('invalid start byte')
		return C1218IdentRequest()

class C1218TerminateRequest(C1218Request):
	terminate = b'\x21'

	def build(self):
		return self.terminate

	@staticmethod
	def parse(data):
		if len(data) != 1:
			raise Exception('invalid data (size)')
		if data[0] != b'\x21':
			raise Exception('invalid start byte')
		return C1218TerminateRequest()

class C1218ReadRequest(C1218Request):
	read = b'\x30'
	__tableid__ = b'\x00\x01'
	__offset__ = b''
	__octetcount__ = b''

	def __init__(self, tableid, offset=None, octetcount=None):
		self.set_tableid(tableid)
		if offset is not None or octetcount is not None:
			self.read = b'\x3f'
			self.set_offset(offset or 0)
			self.set_octetcount(octetcount or 0)

	def build(self):
		return self.read + self.__tableid__ + self.__offset__ + self.__octetcount__

	@staticmethod
	def parse(data):
		if (data[0] == b'\x30' and len(data) < 3) or (data[0] == b'\x3f' and len(data) < 8):
			raise Exception('invalid data (size)')
		if data[0] != b'\x30' and data[0] != b'\x3f':
			raise Exception('invalid start byte')
		tableid = struct.unpack('>H', data[1:3])[0]
		if data[0] == b'\x30':
			offset = None
			octetcount = None
		elif data[0] == b'\x3f':
			offset = struct.unpack('>I', b'\x00' + data[3:6])[0]
			octetcount = struct.unpack('>H', data[6:8])[0]
		request = C1218ReadRequest(tableid, offset, octetcount)
		request.read = data[0]
		return request

	def set_tableid(self, tableid):
		self.__tableid__ = struct.pack('>H', tableid)

	@property
	def tableid(self):
		return struct.unpack('>H', self.__tableid__)[0]

	def set_offset(self, offset):
		if self.__octetcount__ and self.__offset__:
			self.read = b'\x3f'
		self.__offset__ = struct.pack('>I', (offset & 0xffffff))[1:]

	@property
	def offset(self):
		if self.__offset__ == b'':
			return None
		return struct.unpack('>I', b'\x00' + self.__offset__)[0]

	def set_octetcount(self, octetcount):
		if self.__octetcount__ and self.__offset__:
			self.read = b'\x3f'
		self.__octetcount__ = struct.pack('>H', octetcount)

	@property
	def octetcount(self):
		if self.__octetcount__ == b'':
			return None
		return struct.unpack('>H', self.__octetcount__)[0]

class C1218WriteRequest(C1218Request):
	write = b'\x40'
	__tableid__ = b'\x00\x01'
	__offset__ = b''
	__datalen__ = b'\x00\x00'
	__data__ = b''
	__crc8__ = b''

	def __init__(self, tableid, data, offset=None):
		self.set_tableid(tableid)
		self.set_data(data)
		if offset is not None and offset != 0:
			self.write = b'\x4f'
			self.set_offset(offset)

	def build(self):
		packet = self.write
		packet += self.__tableid__
		packet += self.__offset__
		packet += self.__datalen__
		packet += self.__data__
		packet += data_checksum(self.__data__)
		return packet

	@staticmethod
	def parse(data):
		if len(data) < 3:
			raise Exception('invalid data (size)')
		if data[0] != b'\x40' and data[0] != b'\x4f':
			raise Exception('invalid start byte')
		tableid = struct.unpack('>H', data[1:3])[0]
		chksum = data[-1]
		if data[0] == b'\x40':
			table_data = data[5:-1]
			offset = None
		elif data[0] == b'\x4f':
			table_data = data[8:-1]
			offset = struct.unpack('>I', b'\x00' + data[3:6])[0]
		if check_data_checksum(table_data, chksum):
			raise Exception('invalid check sum')
		request = C1218WriteRequest(tableid, table_data, offset=offset)
		request.write = data[0]
		return request

	def set_tableid(self, tableid):
		self.__tableid__ = struct.pack('>H', tableid)

	@property
	def tableid(self):
		return struct.unpack('>H', self.__tableid__)[0]

	def set_offset(self, offset):
		self.__offset__ = struct.pack('>I', (offset & 0xffffff))[1:]

	@property
	def offset(self):
		if self.__offset__ == b'':
			return None
		return struct.unpack('>I', b'\x00' + self.__offset__)[0]

	def set_data(self, data):
		self.__data__ = data
		self.__datalen__ = struct.pack('>H', len(data))

	@property
	def data(self):
		return self.__data__

class C1218Packet(C1218Request):
	start = b'\xee'
	identity = b'\x00'
	control = b'\x00'
	sequence = b'\x00'
	__length__ = b'\x00\x00'  # can never exceed 8183
	__data__ = b''

	@staticmethod
	def parse(data):
		if len(data) < 8:
			raise Exception('invalid data (size)')
		if data[0] != b'\xee':
			raise Exception('invalid start byte')
		identity = data[1]
		control = ord(data[2])
		sequence = data[3]
		length = struct.unpack('>H', data[4:6])[0]
		chksum = data[-2:]
		if packet_checksum(data[:-2]) != chksum:
			raise Exception('invalid check sum')
		data = data[6:-2]
		if ord(data[0]) in C1218_REQUEST_IDS:
			data = C1218_REQUEST_IDS[ord(data[0])].parse(data)
		frame = C1218Packet(data, control, length)
		frame.identity = identity
		frame.sequence = sequence
		return frame

	def __init__(self, data=None, control=None, length=None):
		if data:
			self.set_data(data)
		if length:
			self.set_length(length)
		if control:
			self.set_control(control)

	def __repr__(self):
		if isinstance(self.__data__, C1218Request):
			repr_data = repr(self.__data__)
		else:
			repr_data = '0x' + binascii.b2a_hex(self.__data__).decode('utf-8')
		return '<C1218Packet data=' + repr_data + ' data_len=' + str(len(self.__data__)) + ' crc=0x' + binascii.b2a_hex(packet_checksum(self.start + self.identity + self.control + self.sequence + self.__length__ + self.__data__)).decode('utf-8') + ' >'

	@property
	def data(self):
		return self.__data__

	@data.setter
	def data(self, value):
		self.set_data(value)

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
		self.__data__ = data
		self.set_length(len(self.__data__))

	def set_length(self, length):
		if length > 8183:
			raise ValueError('length can not exceed 8183')
		self.__length__ = struct.pack('>H', length)

	def build(self):
		packet = self.start
		packet += self.identity
		packet += self.control
		packet += self.sequence
		packet += self.__length__
		packet += self.__data__
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
