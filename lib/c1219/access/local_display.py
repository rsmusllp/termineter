#  c1219/access/local_display.py
#
#  Copyright 2016 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
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
