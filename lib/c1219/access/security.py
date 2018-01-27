#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c1219/access/security.py
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

from c1218.errors import C1218ReadTableError
from c1219.constants import *
from c1219.data import get_table_idcb_field
from c1219.errors import C1219ParseError

class C1219SecurityAccess(object):  # Corresponds To Decade 4x
	"""
	This class provides generic access to the security configuration tables
	that are stored in the decade 4x tables.
	"""
	def __init__(self, conn):
		"""
		Initializes a new instance of the class and reads tables from the
		corresponding decades to populate information.

		@type conn: c1218.connection.Connection
		@param conn: The driver to be used for interacting with the
		necessary tables.
		"""
		self.conn = conn
		act_security_table = conn.get_table_data(ACT_SECURITY_LIMITING_TBL)
		security_table = conn.get_table_data(SECURITY_TBL)
		access_ctl_table = conn.get_table_data(ACCESS_CONTROL_TBL)
		try:
			key_table = conn.get_table_data(KEY_TBL)
		except C1218ReadTableError:
			key_table = None

		if len(act_security_table) < 6:
			raise C1219ParseError('expected to read more data from ACT_SECURITY_LIMITING_TBL', ACT_SECURITY_LIMITING_TBL)

		### Parse ACT_SECURITY_LIMITING_TBL ###
		self._nbr_passwords = act_security_table[0]
		self._password_len = act_security_table[1]
		self._nbr_keys = act_security_table[2]
		self._key_len = act_security_table[3]
		self._nbr_perm_used = struct.unpack(self.conn.c1219_endian + 'H', act_security_table[4:6])[0]

		### Parse SECURITY_TBL ###
		if len(security_table) != ((self.nbr_passwords * self.password_len) + self.nbr_passwords):
			raise C1219ParseError('expected to read more data from SECURITY_TBL', SECURITY_TBL)
		self._passwords = {}
		tmp = 0
		while tmp < self.nbr_passwords:
			self._passwords[tmp] = {'idx': tmp, 'password': security_table[:self.password_len], 'groups': security_table[self.password_len]}
			security_table = security_table[self.password_len + 1:]
			tmp += 1

		### Parse ACCESS_CONTROL_TBL ###
		if len(access_ctl_table) != (self.nbr_perm_used * 4):
			raise C1219ParseError('expected to read more data from ACCESS_CONTROL_TBL', ACCESS_CONTROL_TBL)
		self._table_permissions = {}
		self._procedure_permissions = {}
		tmp = 0
		while tmp < self.nbr_perm_used:
			(proc_nbr, std_vs_mfg, proc_flag, flag1, flag2, flag3) = get_table_idcb_field(self.conn.c1219_endian, access_ctl_table)
			if proc_flag:
				self._procedure_permissions[proc_nbr] = {'idx': proc_nbr, 'mfg': std_vs_mfg, 'anyread': flag1, 'anywrite': flag2, 'read': access_ctl_table[2], 'write': access_ctl_table[3]}
			else:
				self._table_permissions[proc_nbr] = {'idx': proc_nbr, 'mfg': std_vs_mfg, 'anyread': flag1, 'anywrite': flag2, 'read': access_ctl_table[2], 'write': access_ctl_table[3]}
			access_ctl_table = access_ctl_table[4:]
			tmp += 1

		### Parse KEY_TBL ###
		self._keys = {}
		if key_table is not None:
			if len(key_table) != (self.nbr_keys * self.key_len):
				raise C1219ParseError('expected to read more data from KEY_TBL', KEY_TBL)
			tmp = 0
			while tmp < self.nbr_keys:
				self._keys[tmp] = key_table[:self.key_len]
				key_table = key_table[self.key_len:]
				tmp += 1

	@property
	def nbr_passwords(self):
		return self._nbr_passwords

	@property
	def password_len(self):
		return self._password_len

	@property
	def nbr_keys(self):
		return self._nbr_keys

	@property
	def key_len(self):
		return self._key_len

	@property
	def nbr_perm_used(self):
		return self._nbr_perm_used

	@property
	def passwords(self):
		return self._passwords

	@property
	def table_permissions(self):
		return self._table_permissions

	@property
	def procedure_permissions(self):
		return self._procedure_permissions

	@property
	def keys(self):
		return self._keys
