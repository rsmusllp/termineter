#  c1218/connection.py
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

from binascii import hexlify, unhexlify
from struct import pack, unpack
from random import randint
from time import sleep
import logging
import serial
from c1218.data import *
from c1218.utils import find_strings, data_chksum_str
from c1218.errors import C1218IOError, C1218ReadTableError, C1218WriteTableError
from c1219.data import c1219ProcedureInit
from c1219.errors import C1219ProcedureError

ERROR_CODE_DICT = {1:'err (Error)', 2:'sns (Service Not Supported)', 3:'isc (Insufficient Security Clearance)', 4:'onp (Operation Not Possible)', 5:'iar (Inappropriate Action Requested)', 6:'bsy (Device Busy)', 7:'dnr (Data Not Ready)', 8:'dlk (Data Locked)', 9:'rno (Renegotiate Request)', 10:'isss (Invalid Service Sequence State)'}

class Connection:
	__toggle_bit__ = False
	# TODO add in the ability to cache a few read-only tables, such as the general config table
	# Read only tables to cache: 0, 1
	def __init__(self, device, settings = None, toggle_control = True, enable_cache = True):
		self.logger = logging.getLogger('c1218.connection')
		self.loggerio = logging.getLogger('c1218.connection.io')
		self.toggle_control = toggle_control
		if hasattr(serial, 'serial_for_url'):
			self.serial_h = serial.serial_for_url(device)
		else:
			self.logger.warning('serial library does not have serial_for_url functionality, it\'s not the latest version')
			self.serial_h = serial.device(device)
		self.logger.debug('successfully opened serial device: ' + device)
		if settings:
			self.logger.debug('applying pySerial settings dictionary')
			self.serial_h.applySettingsDict(settings)
		
		self.serial_h.setRTS(True)
		self.logger.debug('set RTS to True')
		self.serial_h.setDTR(False)
		self.logger.debug('set DTR to False')
		self.logged_in = False
		self.__initialized__ = False
		self.c1219_endian = '<'
		self.caching_enabled = enable_cache
		self.__cacheable_tbls__ = [0, 1]
		self.__tbl_cache__ = {}
		if enable_cache:
			self.logger.info('selective table caching has been enabled')
	
	def __repr__(self):
		return '<' + self.__class__.__name__ + ' Device: ' + self.serial_h.name + ' >'
	
	def flush(self):
		self.logger.info('flushing I/O buffers')
		self.serial_h.flushOutput()
		self.serial_h.flushInput()
		
	def send(self, data):
		if not isinstance(data, Packet):
			data = Packet(data)
		if self.toggle_control:	# bit wise, fuck yeah
			if self.__toggle_bit__:
				data.control = chr(ord(data.control) | 0x20)
				self.__toggle_bit__ = False
			elif not self.__toggle_bit__:
				if ord(data.control) & 0x20:
					data.control = chr(ord(data.control) ^ 0x20)
				self.__toggle_bit__ = True
		elif self.toggle_control and not isinstance(data, Packet):
			self.loggerio.warning('toggle bit is on but the data is not a Packet instance')
		data = str(data)
		self.loggerio.debug('sending frame, length: ' + str(len(data)) + ' data: ' + hexlify(data))
		for pktcount in xrange(0, 3):
			self.write(data)
			response = self.serial_h.read(1)
			if response == NACK:
				self.loggerio.warning('received a NACK after writing data')
				sleep(0.10)
			elif response == '':
				self.loggerio.error('received empty response after writing data')
				sleep(0.10)
			elif response != ACK:
				self.loggerio.error('received unknown response: ' + hex(ord(response)) + ' after writing data')
			else:
				return
		self.loggerio.critical('failed 3 times to correctly send a frame')
		raise C1218IOError('failed 3 times to correctly send a frame')
	
	def recv(self):
		payloadbuffer = ''
		tries = 3
		while tries:
			tmpbuffer = self.serial_h.read(1)
			if tmpbuffer != '\xee':
				self.loggerio.error('did not receive \\xee as the first byte of the frame')
				self.loggerio.debug('received \\x' + tmpbuffer.encode('hex') + ' instead')
				tries -= 1
				continue
			tmpbuffer += self.serial_h.read(3)
			sequence = ord(tmpbuffer[-1])
			length = self.serial_h.read(2)
			tmpbuffer += length
			length = unpack('>H', length)[0]
			payload = self.serial_h.read(length)
			tmpbuffer += payload
			chksum = self.serial_h.read(2)
			if chksum == crc_str(tmpbuffer):
				self.serial_h.write(ACK)
				data = tmpbuffer + chksum
				self.loggerio.debug('received frame, length: ' + str(len(data)) + ' data: ' + hexlify(data))
				payloadbuffer += payload
				if sequence == 0:
					return payloadbuffer
				else:
					tries = 3
			else:
				self.serial_h.write(NACK)
				self.loggerio.warning('crc does not match on received frame')
				tries -= 1
		self.loggerio.critical('failed 3 times to correctly receive a frame')
		raise C1218IOError('failed 3 times to correctly receive a frame')
	
	def write(self, data):
		"""Write raw data to the serial connection. The CRC must already be included at the end"""
		return self.serial_h.write(data)
	
	def read(self, size):
		"""Read raw data from the serial connection"""
		data = self.serial_h.read(size)
		self.logger.debug('read data, length: ' + str(len(data)) + ' data: ' + hexlify(data))
		self.serial_h.write(ACK)
		return data
		
	def close(self):
		if self.__initialized__:
			self.stop()
		self.logged_in = False
		return self.serial_h.close()
		
###===###===### Functions Below This Are Non-Critical ###===###===###
###===###===### Convenience functions                 ###===###===###

	def start(self):
		self.send('\x20')	# identity
		data = self.recv()
		if data[0] != '\x00':
			self.logger.error('received incorrect response to identification service request')
			return False

		self.send('\x61\x01\x00\x01\x06')	# sets the baud rate \x61 sets baud \x01\x00 packet size \x01 nbr_packet \x06 is 9600
		data = self.recv()
		if data[0] != '\x00':
			self.logger.error('received incorrect response to negotiate service request')
			return False
		self.__initialized__ = True
		return True
	
	def stop(self):
		if self.__initialized__ == True:
			self.send('\x21')
			data = self.recv()
			if data == '\x00':
				self.__initialized__ = False
				return True
		return False
	
	def login(self, username = '0000', userid = 0, password = None):
		if password != None and len(password) > 20:
			self.logger.error('password longer than 20 characters received')
			raise Exception('password longer than 20 characters, login failed')
		
		self.send(Logon(username, userid))
		data = self.recv()
		if data != '\x00':
			self.logger.error('login failed, user name and user id rejected')
			return False
		
		if password != None:
			self.send(Security(password))
			data = self.recv()
			if data != '\x00':
				self.logger.error('login failed, password rejected')
				return False
		
		self.logged_in = True
		return True
	
	def logoff(self):
		self.send(Logoff())
		data = self.recv()
		if data == '\x00':
			self.__initialized__ = False
			return True
		return False
	
	def getTableData(self, tableid, octetcount = None, offset = None):
		"""Read from a table"""
		if self.caching_enabled and tableid in self.__cacheable_tbls__ and tableid in self.__tbl_cache__.keys():
			self.logger.info('returning cached table #' + str(tableid))
			return self.__tbl_cache__[tableid]
		self.send(Read(tableid, offset, octetcount))
		data = self.recv()
		status = data[0]
		if status != '\x00':
			status = ord(status)
			details = (ERROR_CODE_DICT.get(status) or 'unknown response code')
			self.logger.error('could not read table id: ' + str(tableid) + ', error: ' + details)
			raise C1218ReadTableError('could not read table id: ' + str(tableid) + ', error: ' + details, status)
		if len(data) < 4:
			if len(data) == 0:
				self.logger.error('could not read table id: ' + str(tableid) + ', error: no data was returned')
				raise C1218ReadTableError('could not read table id: ' + str(tableid) + ', error: no data was returned')
			self.logger.error('could not read table id: ' + str(tableid) + ', error: data read was corrupt, invalid length (less than 4)')
			raise C1218ReadTableError('could not read table id: ' + str(tableid) + ', error: data read was corrupt, invalid length (less than 4)')
		length = unpack('>H', data[1:3])[0]
		chksum = data[-1]
		data = data[3:-1]
		if len(data) != length:
			self.logger.error('could not read table id: ' + str(tableid) + ', error: data read was corrupt, invalid length')
			raise C1218ReadTableError('could not read table id: ' + str(tableid) + ', error: data read was corrupt, invalid length')
		if data_chksum_str(data) != chksum:
			self.logger.error('could not read table id: ' + str(tableid) + ', error: data read was corrupt, invalid check sum')
			raise C1218ReadTableError('could not read table id: ' + str(tableid) + ', error: data read was corrupt, invalid checksum')
		if self.caching_enabled and tableid in self.__cacheable_tbls__ and not tableid in self.__tbl_cache__.keys():
			self.logger.info('cacheing table #' + str(tableid))
			self.__tbl_cache__[tableid] = data
		return data

	def setTableData(self, tableid, data, offset = None):
		"""Write to a table"""
		self.send(Write(tableid, data, offset))
		data = self.recv()
		if data[0] != '\x00':
			status = ord(data[0])
			details = (ERROR_CODE_DICT.get(status) or 'unknown response code')
			self.logger.error('could not write data to the table, error: ' + details)
			raise C1218WriteTableError('could not write data to the table, error: ' + details, status)
		return None

	def runProcedure(self, process_number, std_vs_mfg, params = ''):
		seqnum = randint(2, 254)
		self.logger.info('starting procedure: ' + str(process_number) + ' sequence number: ' + str(seqnum) + ' (' + hex(seqnum) + ')')
		procedure_request = str(c1219ProcedureInit(self.c1219_endian, process_number, std_vs_mfg, 0, seqnum, params))
		self.setTableData(7, procedure_request)
		
		response = self.getTableData(8)
		if response[:3] == procedure_request[:3]:
			return ord(response[3]), response[4:]
		else:
			self.logger.error('invalid response from procedure response table (table #8)')
			raise C1219ProcedureError('invalid response from procedure response table (table #8)')
