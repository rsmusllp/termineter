#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c1219/access/general.py
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

from c1218.data import C1218WriteRequest
from c1218.errors import C1218ReadTableError
from c1219.constants import *
from c1219.errors import C1219ParseError

class C1219GeneralAccess(object):  # Corresponds To Decade 0x
	"""
	This class provides generic access to the general configuration tables
	that are stored in the decade 0x tables.
	"""
	def __init__(self, conn):
		"""
		Initializes a new instance of the class and reads tables from the
		corresponding decades to populate information.

		@type conn: c1218.connection.Connection
		@param conn: The driver to be used for interacting with the
		necessary tables.
		"""
		self._ed_mode = None
		self._std_status = None
		self._device_id = None
		self.conn = conn
		general_config_table = conn.get_table_data(GEN_CONFIG_TBL)
		general_mfg_table = conn.get_table_data(GENERAL_MFG_ID_TBL)
		try:
			mode_status_table = conn.get_table_data(ED_MODE_STATUS_TBL)
		except C1218ReadTableError:
			mode_status_table = None
		try:
			ident_table = conn.get_table_data(DEVICE_IDENT_TBL)
		except C1218ReadTableError:
			ident_table = None

		if len(general_config_table) < 19:
			raise C1219ParseError('expected to read more data from GEN_CONFIG_TBL', GEN_CONFIG_TBL)
		if len(general_mfg_table) < 17:
			raise C1219ParseError('expected to read more data from GENERAL_MFG_ID_TBL', GENERAL_MFG_ID_TBL)
		if mode_status_table and len(mode_status_table) < 5:
			raise C1219ParseError('expected to read more data from ED_MODE_STATUS_TBL', ED_MODE_STATUS_TBL)

		### Parse GEN_CONFIG_TBL ###
		self._char_format = {1: 'ISO/IEC 646 (7-bit)', 2: 'ISO 8859/1 (Latin 1)', 3: 'UTF-8', 4: 'UTF-16', 5: 'UTF-32'}.get((general_config_table[0] & 14) >> 1) or 'Unknown'
		encoding = self.encoding
		self._nameplate_type = {0: 'Gas', 1: 'Water', 2: 'Electric'}.get(general_config_table[7]) or 'Unknown'
		self._id_form = general_config_table[1] & 32
		self._std_version_no = general_config_table[11]
		self._std_revision_no = general_config_table[12]
		self._dim_std_tables_used = general_config_table[13]
		self._dim_mfg_tables_used = general_config_table[14]
		self._dim_std_proc_used = general_config_table[15]
		self._dim_mfg_proc_used = general_config_table[16]

		self._std_tables_used = []
		tmp_data = general_config_table[19:]
		for p in range(self._dim_std_tables_used):
			for i in range(7):
				if tmp_data[p] & (2 ** i):
					self._std_tables_used.append(i + (p * 8))

		self._mfg_tables_used = []
		tmp_data = tmp_data[self._dim_std_tables_used:]
		for p in range(self._dim_mfg_tables_used):
			for i in range(7):
				if tmp_data[p] & (2 ** i):
					self._mfg_tables_used.append(i + (p * 8))

		self._std_proc_used = []
		tmp_data = tmp_data[self._dim_mfg_tables_used:]
		for p in range(self._dim_std_proc_used):
			for i in range(7):
				if tmp_data[p] & (2 ** i):
					self._std_proc_used.append(i + (p * 8))

		self._mfg_proc_used = []
		tmp_data = tmp_data[self._dim_std_proc_used:]
		for p in range(self._dim_mfg_proc_used):
			for i in range(7):
				if tmp_data[p] & (2 ** i):
					self._mfg_proc_used.append(i + (p * 8))

		### Parse GENERAL_MFG_ID_TBL ###
		self._manufacturer = general_mfg_table[0:4].rstrip().decode(encoding)
		self._ed_model = general_mfg_table[4:12].rstrip().decode(encoding)
		self._hw_version_no = general_mfg_table[12]
		self._hw_revision_no = general_mfg_table[13]
		self._fw_version_no = general_mfg_table[14]
		self._fw_revision_no = general_mfg_table[15]
		if self._id_form == 0:
			self._mfg_serial_no = general_mfg_table[16:32].strip()
		else:
			self._mfg_serial_no = general_mfg_table[16:24]
		self._mfg_serial_no = self._mfg_serial_no.decode(encoding)

		### Parse ED_MODE_STATUS_TBL ###
		if mode_status_table:
			self._ed_mode = mode_status_table[0]
			self._std_status = struct.unpack(conn.c1219_endian + 'H', mode_status_table[1:3])[0]

		### Parse DEVICE_IDENT_TBL ###
		if ident_table:
			if self._id_form == 0 and len(ident_table) != 20:
				raise C1219ParseError('expected to read more data from DEVICE_IDENT_TBL', DEVICE_IDENT_TBL)
			elif self._id_form != 0 and len(ident_table) != 10:
				raise C1219ParseError('expected to read more data from DEVICE_IDENT_TBL', DEVICE_IDENT_TBL)
			self._device_id = ident_table.strip().decode(encoding)

	def set_device_id(self, newid):
		if self._id_form == 0:
			newid += ' ' * (20 - len(newid))
		else:
			newid += ' ' * (10 - len(newid))
		newid = newid.encode(self.encoding)
		self.conn.set_table_data(DEVICE_IDENT_TBL, newid)

		self.conn.send(C1218WriteRequest(PROC_INITIATE_TBL, b'\x46\x08\x1c\x03\x0b\x0c\x09\x0f\x12'))
		data = self.conn.recv()
		if data != b'\x00':
			pass

		try:
			ident_table = self.conn.get_table_data(DEVICE_IDENT_TBL)
		except C1218ReadTableError:
			return 1

		if self._id_form == 0 and len(ident_table) != 20:
			raise C1219ParseError('expected to read more data from DEVICE_IDENT_TBL', DEVICE_IDENT_TBL)
		elif self._id_form != 0 and len(ident_table) != 10:
			raise C1219ParseError('expected to read more data from DEVICE_IDENT_TBL', DEVICE_IDENT_TBL)
		if not ident_table.startswith(newid):
			return 2
		self._device_id = newid
		return 0

	@property
	def encoding(self):
		return {2: 'iso-8859-1', 4: 'utf-16', 5: 'utf-32'}.get(self._char_format, 'utf-8')

	@property
	def char_format(self):
		return self._char_format

	@property
	def nameplate_type(self):
		return self._nameplate_type

	@property
	def id_form(self):
		return self._id_form

	@property
	def std_version_no(self):
		return self._std_version_no

	@property
	def std_revision_no(self):
		return self._std_revision_no

	@property
	def std_tbls_used(self):
		return self._std_tables_used

	@property
	def mfg_tbls_used(self):
		return self._mfg_tables_used

	@property
	def std_proc_used(self):
		return self._std_proc_used

	@property
	def mfg_proc_used(self):
		return self._mfg_proc_used

	@property
	def manufacturer(self):
		return self._manufacturer

	@property
	def ed_model(self):
		return self._ed_model

	@property
	def hw_version_no(self):
		return self._hw_version_no

	@property
	def hw_revision_no(self):
		return self._hw_revision_no

	@property
	def fw_version_no(self):
		return self._fw_version_no

	@property
	def fw_revision_no(self):
		return self._fw_revision_no

	@property
	def mfg_serial_no(self):
		return self._mfg_serial_no

	@property
	def ed_mode(self):
		return self._ed_mode

	@property
	def std_status(self):
		return self._std_status

	@property
	def device_id(self):
		return self._device_id
