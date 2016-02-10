#  c1219/access/telephone.py
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

#  This library contains classes to facilitate retreiving complex C1219
#  tables from a target device.  Each parser expects to be passed a
#  connection object.  Right now the connection object is a
#  c1218.connection.Connection instance, but anythin implementing the basic
#  methods should work.

from __future__ import unicode_literals

import struct

from c1219.constants import *
from c1219.errors import C1219ParseError, C1219ProcedureError

class C1219TelephoneAccess(object):	# Corresponds To Decade 9x
	"""
	This class provides generic access to the telephone/modem configuration
	tables that are stored in the decade 9x tables.
	"""
	__global_bit_rate__ = None
	__originate_bit_rate__ = None
	__answer_bit_rate__ = None
	__prefix_number__ = ''
	__primary_phone_number_idx__ = None
	__secondary_phone_number_idx__ = None

	def __init__(self, conn):
		"""
		Initializes a new instance of the class and reads tables from the
		corresponding decades to populate information.

		@type conn: c1218.connection.Connection
		@param conn: The driver to be used for interacting with the
		necessary tables.
		"""
		self.conn = conn
		actual_telephone_table = self.conn.get_table_data(ACT_TELEPHONE_TBL)
		global_parameters_table = self.conn.get_table_data(GLOBAL_PARAMETERS_TBL)
		originate_parameters_table = self.conn.get_table_data(ORIGINATE_PARAMETERS_TBL)
		originate_schedule_table = self.conn.get_table_data(ORIGINATE_SCHEDULE_TBL)
		answer_parameters_table = self.conn.get_table_data(ANSWER_PARAMETERS_TBL)

		if (actual_telephone_table) < 14:
			raise C1219ParseError('expected to read more data from ACT_TELEPHONE_TBL', ACT_TELEPHONE_TBL)

		info = {}
		### Parse ACT_TELEPHONE_TBL ###
		use_extended_status = bool(actual_telephone_table[0] & 128)
		prefix_length = actual_telephone_table[4]
		nbr_originate_numbers = actual_telephone_table[5]
		phone_number_length = actual_telephone_table[6]
		bit_rate_settings = (actual_telephone_table[1] >> 3) & 3		# not the actual settings but rather where they are defined
		self.__can_answer__ = bool(actual_telephone_table[0] & 1)
		self.__use_extended_status__ = use_extended_status
		self.__nbr_originate_numbers__ = nbr_originate_numbers

		### Parse GLOBAL_PARAMETERS_TBL ###
		self.__psem_identity__ = global_parameters_table[0]
		if bit_rate_settings == 1:
			if len(global_parameters_table) < 5:
				raise C1219ParseError('expected to read more data from GLOBAL_PARAMETERS_TBL', GLOBAL_PARAMETERS_TBL)
			self.__global_bit_rate__ = struct.unpack(conn.c1219_endian + 'I', global_parameters_table[1:5])[0]

		### Parse ORIGINATE_PARAMETERS_TBL ###
		if bit_rate_settings == 2:
			self.__originate_bit_rate__ = struct.unpack(conn.c1219_endian + 'I', originate_parameters_table[0:4])[0]
			originate_parameters_table = originate_parameters_table[4:]
		self.__dial_delay__ = originate_parameters_table[0]
		originate_parameters_table = originate_parameters_table[1:]

		if prefix_length != 0:
			self.__prefix_number__ = originate_parameters_table[:prefix_length]
			originate_parameters_table = originate_parameters_table[prefix_length:]

		self.__originating_numbers__ = {}
		tmp = 0
		while tmp < self.__nbr_originate_numbers__:
			self.__originating_numbers__[tmp] = {'idx': tmp, 'number': originate_parameters_table[:phone_number_length], 'status': None}
			originate_parameters_table = originate_parameters_table[phone_number_length:]
			tmp += 1

		### Parse ORIGINATE_SHCEDULE_TBL ###
		primary_phone_number_idx = originate_schedule_table[0] & 7
		secondary_phone_number_idx = (originate_schedule_table[0] >> 4) & 7
		if primary_phone_number_idx < 7:
			self.__primary_phone_number_idx__ = primary_phone_number_idx
		if secondary_phone_number_idx < 7:
			self.__secondary_phone_number_idx__ = secondary_phone_number_idx

		### Prase ANSWER_PARAMETERS_TBL ###
		if bit_rate_settings == 2:
			self.__answer_bit_rate__ = struct.unpack(conn.c1219_endian + 'I', answer_parameters_table[0:4])[0]
		self.update_last_call_statuses()

	def initiate_call(self, number=None, idx=None):
		if number:
			idx = None
			for tmpidx in self.__originating_numbers__.keys():
				if self.__originating_numbers__[tmpidx]['number'] == number:
					idx = tmpidx
			if idx is None:
				raise C1219ProcedureError('target phone number not found in originating numbers')
		if not idx in self.__originating_numbers__.keys():
			raise C1219ProcedureError('phone number index not within originating numbers range')
		return self.initiate_call_ex(self.conn, idx)

	@staticmethod
	def initiate_call_ex(conn, idx):
		return conn.run_procedure(20, False, struct.pack('B', idx))

	def update_last_call_statuses(self):
		tmp = 0
		call_status_table = self.conn.get_table_data(CALL_STATUS_TBL)
		if (len(call_status_table) % self.nbr_originate_numbers) != 0:
			raise C1219ParseError('expected to read more data from CALL_STATUS_TBL', CALL_STATUS_TBL)
		call_status_rcd_length = (len(call_status_table) / self.nbr_originate_numbers)
		while tmp < self.nbr_originate_numbers:
			self.__originating_numbers__[tmp]['status'] = call_status_table[0]
			call_status_table = call_status_table[call_status_rcd_length:]
			tmp += 1

	@property
	def answer_bit_rate(self):
		return self.__answer_bit_rate__

	@property
	def can_answer(self):
		return self.__can_answer__

	@property
	def dial_delay(self):
		return self.__dial_delay__

	@property
	def global_bit_rate(self):
		return self.__global_bit_rate__

	@property
	def nbr_originate_numbers(self):
		return self.__nbr_originate_numbers__

	@property
	def originate_bit_rate(self):
		return self.__originate_bit_rate__

	@property
	def originating_numbers(self):
		return self.__originating_numbers__

	@property
	def prefix_number(self):
		return self.__prefix_number__

	@property
	def primary_phone_number_idx(self):
		return self.__primary_phone_number_idx__

	@property
	def psem_identity(self):
		return self.__psem_identity__

	@property
	def secondary_phone_number_idx(self):
		return self.__secondary_phone_number_idx__

	@property
	def use_extended_status(self):
		return self.__use_extended_status__
