#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c1219/access/telephone.py
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
	def __init__(self, conn):
		"""
		Initializes a new instance of the class and reads tables from the
		corresponding decades to populate information.

		@type conn: c1218.connection.Connection
		@param conn: The driver to be used for interacting with the
		necessary tables.
		"""
		self._global_bit_rate = None
		self._originate_bit_rate = None
		self._answer_bit_rate = None
		self._prefix_number = ''
		self._primary_phone_number_idx = None
		self._secondary_phone_number_idx = None
		self.conn = conn
		actual_telephone_table = self.conn.get_table_data(ACT_TELEPHONE_TBL)
		global_parameters_table = self.conn.get_table_data(GLOBAL_PARAMETERS_TBL)
		originate_parameters_table = self.conn.get_table_data(ORIGINATE_PARAMETERS_TBL)
		originate_schedule_table = self.conn.get_table_data(ORIGINATE_SCHEDULE_TBL)
		answer_parameters_table = self.conn.get_table_data(ANSWER_PARAMETERS_TBL)

		if (actual_telephone_table) < 14:
			raise C1219ParseError('expected to read more data from ACT_TELEPHONE_TBL', ACT_TELEPHONE_TBL)

		### Parse ACT_TELEPHONE_TBL ###
		use_extended_status = bool(actual_telephone_table[0] & 128)
		prefix_length = actual_telephone_table[4]
		nbr_originate_numbers = actual_telephone_table[5]
		phone_number_length = actual_telephone_table[6]
		bit_rate_settings = (actual_telephone_table[1] >> 3) & 3		# not the actual settings but rather where they are defined
		self._can_answer = bool(actual_telephone_table[0] & 1)
		self._use_extended_status = use_extended_status
		self._nbr_originate_numbers = nbr_originate_numbers

		### Parse GLOBAL_PARAMETERS_TBL ###
		self._psem_identity = global_parameters_table[0]
		if bit_rate_settings == 1:
			if len(global_parameters_table) < 5:
				raise C1219ParseError('expected to read more data from GLOBAL_PARAMETERS_TBL', GLOBAL_PARAMETERS_TBL)
			self._global_bit_rate = struct.unpack(conn.c1219_endian + 'I', global_parameters_table[1:5])[0]

		### Parse ORIGINATE_PARAMETERS_TBL ###
		if bit_rate_settings == 2:
			self._originate_bit_rate = struct.unpack(conn.c1219_endian + 'I', originate_parameters_table[0:4])[0]
			originate_parameters_table = originate_parameters_table[4:]
		self._dial_delay = originate_parameters_table[0]
		originate_parameters_table = originate_parameters_table[1:]

		if prefix_length != 0:
			self._prefix_number = originate_parameters_table[:prefix_length]
			originate_parameters_table = originate_parameters_table[prefix_length:]

		self._originating_numbers = {}
		tmp = 0
		while tmp < self._nbr_originate_numbers:
			self._originating_numbers[tmp] = {'idx': tmp, 'number': originate_parameters_table[:phone_number_length], 'status': None}
			originate_parameters_table = originate_parameters_table[phone_number_length:]
			tmp += 1

		### Parse ORIGINATE_SHCEDULE_TBL ###
		primary_phone_number_idx = originate_schedule_table[0] & 7
		secondary_phone_number_idx = (originate_schedule_table[0] >> 4) & 7
		if primary_phone_number_idx < 7:
			self._primary_phone_number_idx = primary_phone_number_idx
		if secondary_phone_number_idx < 7:
			self._secondary_phone_number_idx = secondary_phone_number_idx

		### Prase ANSWER_PARAMETERS_TBL ###
		if bit_rate_settings == 2:
			self._answer_bit_rate = struct.unpack(conn.c1219_endian + 'I', answer_parameters_table[0:4])[0]
		self.update_last_call_statuses()

	def initiate_call(self, number=None, idx=None):
		if number:
			idx = None
			for tmpidx in self._originating_numbers.keys():
				if self._originating_numbers[tmpidx]['number'] == number:
					idx = tmpidx
			if idx is None:
				raise C1219ProcedureError('target phone number not found in originating numbers')
		if not idx in self._originating_numbers.keys():
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
			self._originating_numbers[tmp]['status'] = call_status_table[0]
			call_status_table = call_status_table[call_status_rcd_length:]
			tmp += 1

	@property
	def answer_bit_rate(self):
		return self._answer_bit_rate

	@property
	def can_answer(self):
		return self._can_answer

	@property
	def dial_delay(self):
		return self._dial_delay

	@property
	def global_bit_rate(self):
		return self._global_bit_rate

	@property
	def nbr_originate_numbers(self):
		return self._nbr_originate_numbers

	@property
	def originate_bit_rate(self):
		return self._originate_bit_rate

	@property
	def originating_numbers(self):
		return self._originating_numbers

	@property
	def prefix_number(self):
		return self._prefix_number

	@property
	def primary_phone_number_idx(self):
		return self._primary_phone_number_idx

	@property
	def psem_identity(self):
		return self._psem_identity

	@property
	def secondary_phone_number_idx(self):
		return self._secondary_phone_number_idx

	@property
	def use_extended_status(self):
		return self._use_extended_status
