#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c1219/data.py
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

import struct
import time

from c1219.constants import *

def format_ltime(endianess, tm_format, data):
	"""
	Return data formatted into a human readable time stamp.

	:param str endianess: The endianess to use when packing values ('>' or '<')
	:param int tm_format: The format that the data is packed in, this typically
	  corresponds with the value in the GEN_CONFIG_TBL (table #0) (1 <= tm_format <= 4)
	:param bytes data: The packed and machine-formatted data to parse
	:rtype: str
	"""
	if tm_format == 0:
		return ''
	elif tm_format == 1 or tm_format == 2:  # I can't find solid documentation on the BCD data-type
		y = data[0]
		year = '????'
		if 90 <= y <= 99:
			year = '19' + str(y)
		elif 0 <= y <= 9:
			year = '200' + str(y)
		elif 10 <= y <= 89:
			year = '20' + str(y)
		month = data[1]
		day = data[2]
		hour = data[3]
		minute = data[4]
		second = data[5]
	elif tm_format == 3 or tm_format == 4:
		if tm_format == 3:
			u_time = float(struct.unpack(endianess + 'I', data[0:4])[0])
			second = float(data[4])
			final_time = time.gmtime((u_time * 60) + second)
		elif tm_format == 4:
			final_time = time.gmtime(float(struct.unpack(endianess + 'I', data[0:4])[0]))
		year = str(final_time.tm_year)
		month = str(final_time.tm_mon)
		day = str(final_time.tm_mday)
		hour = str(final_time.tm_hour)
		minute = str(final_time.tm_min)
		second = str(final_time.tm_sec)

	return "{0} {1} {2} {3}:{4}:{5}".format((MONTHS.get(month) or 'UNKNOWN'), day, year, hour, minute, second)

def get_history_entry_record(endianess, hist_date_time_flag, tm_format, event_number_flag, hist_seq_nbr_flag, data):
	"""
	Return data formatted into a log entry.

	:param str endianess: The endianess to use when packing values ('>' or '<')
	:param bool hist_date_time_flag: Whether or not a time stamp is included.
	:param int tm_format: The format that the data is packed in, this typically
	  corresponds with the value in the GEN_CONFIG_TBL (table #0) (1 <= tm_format <= 4)
	:param bool event_number_flag: Whether or not an event number is included.
	:param bool hist_seq_nbr_flag: Whether or not an history sequence number
	  is included.
	:param str data: The packed and machine-formatted data to parse
	:rtype: dict
	"""
	rcd = {}
	if hist_date_time_flag:
		tmstmp = format_ltime(endianess, tm_format, data[0:LTIME_LENGTH.get(tm_format)])
		if tmstmp:
			rcd['Time'] = tmstmp
		data = data[LTIME_LENGTH.get(tm_format):]
	if event_number_flag:
		rcd['Event Number'] = struct.unpack(endianess + 'H', data[:2])[0]
		data = data[2:]
	if hist_seq_nbr_flag:
		rcd['History Sequence Number'] = struct.unpack(endianess + 'H', data[:2])[0]
		data = data[2:]
	rcd['User ID'] = struct.unpack(endianess + 'H', data[:2])[0]
	rcd['Procedure Number'], rcd['Std vs Mfg'] = get_table_idbb_field(endianess, data[2:4])[:2]
	rcd['Arguments'] = data[4:]
	return rcd

def get_table_idbb_field(endianess, data):
	"""
	Return data from a packed TABLE_IDB_BFLD bit-field.

	:param str endianess: The endianess to use when packing values ('>' or '<')
	:param str data: The packed and machine-formatted data to parse
	:rtype: tuple
	:return: Tuple of (proc_nbr, std_vs_mfg)
	"""
	bfld = struct.unpack(endianess + 'H', data[:2])[0]
	proc_nbr = bfld & 0x7ff
	std_vs_mfg = bool(bfld & 0x800)
	selector = (bfld & 0xf000) >> 12
	return (proc_nbr, std_vs_mfg, selector)

def get_table_idcb_field(endianess, data):
	"""
	Return data from a packed TABLE_IDC_BFLD bit-field.

	:param str endianess: The endianess to use when packing values ('>' or '<')
	:param str data: The packed and machine-formatted data to parse
	:rtype: tuple
	:return: Tuple of (proc_nbr, std_vs_mfg, proc_flag, flag1, flag2, flag3)
	"""
	bfld = struct.unpack(endianess + 'H', data[:2])[0]
	proc_nbr = bfld & 2047
	std_vs_mfg = bool(bfld & 2048)
	proc_flag = bool(bfld & 4096)
	flag1 = bool(bfld & 8192)
	flag2 = bool(bfld & 16384)
	flag3 = bool(bfld & 32768)
	return (proc_nbr, std_vs_mfg, proc_flag, flag1, flag2, flag3)

class C1219ProcedureInit(object):
	"""
	A C1219 Procedure Request, this data is written to table 7 in order to
	start a procedure.

	:param str endianess: The endianess to use when packing values ('>' or '<')
	:param int table_proc_nbr: The numeric procedure identifier (0 <= table_proc_nbr <= 2047).
	:param bool std_vs_mfg: Whether the procedure is manufacturer specified
	  or not.  True is manufacturer specified.
	:param int selector: Controls how data is returned (0 <= selector <= 15).
	  0: Post response in PROC_RESPONSE_TBL (#8) on completion.
	  1: Post response in PROC_RESPONSE_TBL (#8) on exception.
	  2: Do not post response in PROC_RESPONSE_TBL (#8).
	  3: Post response in PROC_RESPONSE_TBL (#8) immediately and another response in PROC_RESPONSE_TBL (#8) on completion.
	  4-15: Reserved.
	:param int seqnum: The identifier for this procedure to be used for
	  coordination (0x00 <= seqnum <= 0xff).
	:param str params: The parameters to pass to the procedure initiation
	  request.
	"""
	def __init__(self, endianess, table_proc_nbr, std_vs_mfg, selector, seqnum, params=b''):
		mfg_defined = 0
		if std_vs_mfg:
			mfg_defined = 1
		self.mfg_defined = bool(mfg_defined)
		self.selector = selector

		mfg_defined <<= 11
		selector <<= 12

		self.table_idb_bfld = struct.pack(endianess + 'H', (table_proc_nbr | mfg_defined | selector))
		self.endianess = endianess
		self.proc_nbr = table_proc_nbr
		self.seqnum = seqnum
		self.params = params

	def __repr__(self):
		return "<{0} mfg_defined={1} proc_nbr={2} >".format(self.__class__.__name__, self.mfg_defined, self.proc_nbr)

	def __str__(self):
		return self.build()

	def build(self):
		return self.table_idb_bfld + struct.pack('B', self.seqnum) + self.params

	@classmethod
	def from_bytes(cls, endianess, data):
		if len(data) < 3:
			raise Exception('invalid data (size)')
		proc_nbr, std_vs_mfg, selector = get_table_idbb_field(endianess, data[0:2])
		seqnum = data[2]
		return cls(endianess, proc_nbr, std_vs_mfg, selector, seqnum, data[3:])
