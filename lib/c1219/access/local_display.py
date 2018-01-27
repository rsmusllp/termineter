#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c1219/access/local_display.py
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

import collections
import struct

from c1219.access import BaseC1219TableAccess
from c1219.constants import *

DispListDescRcd = collections.namedtuple('DispListDescRcd', ('on_time', 'off_time', 'hold_time', 'default_list', 'nbr_items'))

class C1219LocalDisplayAccess(BaseC1219TableAccess):  # Corresponds To Decade 3x
	_tbl_props = (
		'on_time_flag',
		'off_time_flag',
		'hold_time_flag',
		'nbr_disp_sources',
		'width_disp_sources',
		'nbr_pri_disp_list_items',
		'nbr_pri_disp_lists',
		'nbr_sec_disp_list_items',
		'nbr_sec_disp_lists'
	)
	def __init__(self, conn):
		"""
		Initializes a new instance of the class and reads tables from the
		corresponding decades to populate information.

		@type conn: c1218.connection.Connection
		@param conn: The driver to be used for interacting with the
		necessary tables.
		"""
		self.conn = conn
		act_disp = conn.get_table_data(ACT_DISP_TBL)
		unpacked = struct.unpack('<BHBHBHB', act_disp)
		bfld = unpacked[0]
		self._on_time_flag = bool(bfld & 1)
		self._off_time_flag = bool(bfld & 0b10)
		self._hold_time_flag = bool(bfld & 0b100)
		self._nbr_disp_sources = unpacked[1]
		self._width_disp_sources = unpacked[2]
		self._nbr_pri_disp_list_items = unpacked[3]
		self._nbr_pri_disp_lists = unpacked[4]
		self._nbr_sec_disp_list_items = unpacked[5]
		self._nbr_sec_disp_lists = unpacked[6]

		self.pri_disp_list = []
		pri_disp_list = conn.get_table_data(PRI_DISP_LIST_TBL)
		for _ in range(self._nbr_pri_disp_lists):
			bfld = pri_disp_list[0]
			on_time = bfld & 0b1111
			off_time = (bfld >> 4) & 0b1111
			bfld = pri_disp_list[1]
			hold_time = bfld & 0b1111
			default_list = (bfld >> 4) & 0b1111
			nbr_items = pri_disp_list[2]
			self.pri_disp_list.append(DispListDescRcd(on_time, off_time, hold_time, default_list, nbr_items))
			pri_disp_list = pri_disp_list[3:]

		self.pri_disp_sources = struct.unpack("{0}H".format(self._nbr_pri_disp_list_items), pri_disp_list)
