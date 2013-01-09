#  c1222/data.py
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

from struct import pack, unpack
from c1222.utils import data_chksum, data_chksum_str
from pyasn1.type import tag
from pyasn1.type import univ
from pyasn1.codec.ber import encoder as ber_encoder
from pyasn1.codec.ber import decoder as ber_decoder

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

class C1222Request(object):
	def __repr__(self):
		return '<' + self.__class__.__name__ + ' >'
	
	def __str__(self):
		return self.do_build()
	
	def __len__(self):
		return len(str(self))

	def set_ap_title(self, ap_title):
		if not hasattr(self, '__ap_title__'):
			raise Exception(self.__class__.__name__ + ' does not support the ap_title element')
		if isinstance(ap_title, univ.ObjectIdentifier):
			self.__ap_title__ = ber_encoder.encode(ap_title)
		if isinstance(ap_title, str):
			self.__ap_title__ = ap_title
		else:
			self.__ap_title__ = ber_encoder.encode(univ.ObjectIdentifier(ap_title))

	def set_userid(self, userid):
		if not hasattr(self, '__userid__'):
			raise Exception(self.__class__.__name__ + ' does not support the userid element')
		if isinstance(userid, str) and userid.isdigit():
			userid = int(userid)
		elif not isinstance(userid, int):
			ValueError('userid must be between 0x0000 and 0xffff')
		if not 0x0000 <= userid <= 0xffff:
			raise ValueError('userid must be between 0x0000 and 0xffff')
		self.__userid__ = pack(">H", userid)

class C1222DisconnectRequest(C1222Request):
	disconnect = '\x22'
	
	def do_build(self):
		return self.disconnect

class C1222IdentRequest(C1222Request):
	ident = '\x20'
	
	def do_build(self):
		return self.ident

class C1222LogoffRequest(C1222Request):
	logoff = '\x52'
	
	def do_build(self):
		return self.logoff

class C1222LogonRequest(C1222Request):
	logon = '\x50'
	__userid__ = '\x00\x00'
	__username__ = '\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20'
	__session_idle_timeout__ = '\x00\x00'
	
	def __init__(self, username = '', userid = 0, session_idle_timeout = 0):
		self.set_username(username)
		self.set_userid(userid)
		self.set_session_idle_timeout(session_idle_timeout)

	def do_build(self):
		return self.logon + self.__userid__ + self.__username__ + self.__session_idle_timeout__

	def set_username(self, value):
		if len(value) > 10:
			raise ValueError('username must be 10 characters or less')
		self.__username__ = value + ('\x20' * (10 - len(value)))

	def set_session_idle_timeout(self, session_idle_timeout):
		if not isinstance(session_idle_timeout, int):
			ValueError('session_idle_timeout must be between 0x0000 and 0xffff')
		if not 0x0000 <= session_idle_timeout <= 0xffff:
			raise ValueError('session_idle_timeout must be between 0x0000 and 0xffff')
		self.__session_idle_timeout__ = pack(">H", session_idle_timeout)

class C1222ReadRequest(C1222Request):
	read = '\x30'
	__tableid__ = '\x00\x01'
	__offset__ = ''
	__octetcount__ = ''

	def __init__(self, tableid, offset = None, octetcount = None):
		self.set_tableid(tableid)
		if (offset != None and offset != 0) and (octetcount != None and octetcount != 0):
			self.read = '\x3f'
			self.set_offset(offset)
			self.set_octetcount(octetcount)

	def do_build(self):
		return self.read + self.__tableid__ + self.__offset__ + self.__octetcount__

	def set_tableid(self, tableid):
		self.__tableid__ = pack('>H', tableid)
	
	def set_offset(self, offset):
		self.__offset__ = pack('>I', (offset & 0xffffff))[1:]
	
	def set_octetcount(self, octetcount):
		self.__octetcount__ = pack('>H', octetcount)

class C1222ResolveRequest(C1222Request):
	resolve = '\x25'
	__ap_title__ = ''
	
	def __init__(self, ap_title):
		self.set_ap_title(ap_title)
	
	def do_build(self):
		return self.resolve + self.__ap_title__

class C1222SecurityRequest(C1222Request):
	security = '\x51'
	__password__ = '\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20'
	__userid__ = '\x00\x00'
	
	def __init__(self, password = '', userid = 0):
		self.set_password(password)
		self.set_userid(userid)

	def do_build(self):
		return self.security + self.__password__ + self.__userid__

	def set_password(self, value):
		if len(value) > 20:
			raise ValueError('password must be 20 characters or less')
		self.__password__ = value + ('\x20' * (20 - len(value)))

class C1222TerminateRequest(C1222Request):
	terminate = '\x21'
	
	def do_build(self):
		return self.terminate

class C1222TraceRequest(C1222Request):
	trace = '\x26'
	__ap_title__ = ''
	
	def __init__(self, ap_title):
		self.set_ap_title(ap_title)
	
	def do_build(self):
		return self.trace + self.__ap_title__

class C1222WaitRequest(C1222Request):
	wait = '\x70'
	time = '\x00'
	
	def __init__(self, time = 0):
		self.set_time(time)
	
	def do_build(self):
		return self.wait + self.time
	
	def set_time(self, time):
		self.time = chr(time)

class C1222WriteRequest(C1222Request):
	write = '\x40'
	__tableid__ = '\x00\x01'
	__offset__ = ''
	__datalen__ = '\x00\x00'
	__data__ = ''
	
	def __init__(self, tableid, data, offset = None):
		self.set_tableid(tableid)
		self.set_data(data)
		if offset != None and offset != 0:
			self.write = '\x4f'
			self.set_offset(offset)
	
	def do_build(self):
		packet = self.write
		packet += self.__tableid__
		packet += self.__offset__
		packet += self.__datalen__
		packet += self.__data__
		packet += data_chksum_str(self.__data__)
		return packet
	
	def set_tableid(self, tableid):
		self.__tableid__ = pack('>H', tableid)
	
	def set_offset(self, offset):
		self.__offset__ = pack('>I', (offset & 0xffffff))[1:]
	
	def set_data(self, data):
		self.__data__ = data
		self.__datalen__ = pack('>H', len(data))

class C1222Packet(C1222Request):
	start = '\x60'
	__length__ = '\x00'
	__data__ = ''
	
	@staticmethod
	def parse(data):
		if data[0] != '\x60':
			raise Exception('invalid start byte')
			
		(called_ap, data) = ber_decoder.decode(data)
		(calling_ap, data) = ber_decoder.decode(data)
		(calling_ap_invocation_id , data) = ber_decoder.decode(data)
		
		called_ap = C1222CalledAPTitle(called_ap)
		calling_ap = C1222CallingAPTitle(calling_ap)
		calling_ap_invocation_id = C1222CallingAPInvocationID(calling_ap_invocation_id)
		
		frame = C1222Packet(called_ap, calling_ap, calling_ap_invocation_id, data)
		return frame
	
	def __init__(self, called_ap, calling_ap, calling_ap_invocation_id, data = None, length = None):
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
			self.set_data('')
		if length:
			self.set_length(length)
	
	def __repr__(self):
		return '<C1222Packet data=0x' + str(self.__data__).encode('hex') + ' data_len=' + str(len(self.__data__)) + ' >'
	
	@property
	def data(self):
		return self.__data__
	
	@data.setter
	def data(self, value):
		self.set_data(value)
	
	def set_data(self, value):
		self.__data__ = value
		length  = len(self.called_ap.encode())
		length += len(self.calling_ap.encode())
		length += len(self.calling_ap_invocation_id.encode())
		length += len(str(self.__data__))
		self.set_length(length)
	
	def set_length(self, length):
		self.__length__ = chr(length)
	
	def do_build(self):
		packet  = self.start
		packet += self.__length__
		packet += self.called_ap.encode()
		packet += self.calling_ap.encode()
		packet += self.calling_ap_invocation_id.encode()
		packet += str(self.__data__)
		return packet
