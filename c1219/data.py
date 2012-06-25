#  c1219/data.py
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

import time
from struct import pack, unpack
from c1219.constants import *

def formatLTime(endianess, tm_format, data):
	"""
	Return data formatted into a human readable time stamp.
	
	@type endianess: String ('>' or '<')
	@param endianess: The endianess to use when packing values
	
	@type tm_format: Integer (1 <= tm_format <= 4)
	@param tm_format: The format that the data is packed in, this typically
	corresponds with the value in the GEN_CONFIG_TBL (table #0)
	
	@type data: String
	@param data: The packed and machine-formatted data to parse
	
	@rtype: String
	"""
	if tm_format == 0:
		return ''
	elif tm_format == 1 or tm_format == 2:	# I can't find solid documentation on the BCD data-type
		y = ord(data[0])
		year = '????'
		if 90 <= y <= 99:
			year = '19' + str(y)
		elif 0 <= y <= 9:
			year = '200' + str(y)
		elif 10 <= y <= 89:
			year = '20' + str(y)
		month = ord(data[1])
		day = ord(data[2])
		hour = ord(data[3])
		minute = ord(data[4])
		second = ord(data[5])
	elif tm_format == 3 or tm_format == 4:
		if tm_format == 3:
			u_time = float(unpack(endianess + 'I', data[0:4])[0])
			second = float(data[4])
			final_time = time.gmtime((u_time * 60) + second)
		elif tm_format == 4:
			final_time = time.gmtime(float(unpack(endianess + 'I', data[0:4])[0]))
		year = str(final_time.tm_year)
		month = str(final_time.tm_mon)
		day = str(final_time.tm_mday)
		hour = str(final_time.tm_hour)
		minute = str(final_time.tm_min)
		second = str(final_time.tm_sec)
	
	return "{0} {1} {2} {3}:{4}:{5}".format((MONTHS.get(month) or 'UNKNOWN'), day, year, hour, minute, second)

def getHistoryEntryRcd(endianess, hist_date_time_flag, tm_format, event_number_flag, hist_seq_nbr_flag, data):
	"""
	Return data formatted into a log entry.
	
	@type endianess: String ('>' or '<')
	@param endianess: The endianess to use when packing values
	
	@type hist_date_time_flag: Boolean
	@param hist_date_time_flag: Whether or not a time stamp is included.
	
	@type tm_format: Integer (1 <= tm_format <= 4)
	@param tm_format: The format that the data is packed in, this typically
	corresponds with the value in the GEN_CONFIG_TBL (table #0)
	
	@type event_number_flag: Boolean
	@param event_number_flag: Whether or not an event number is included.
	
	@type hist_seq_nbr_flag: Boolean
	@param hist_seq_nbr_flag: Whether or not an history sequence number
	is included.
	
	@type data: String
	@param data: The packed and machine-formatted data to parse
	
	@rtype: Dictionary Variable-Keys
	"""
	rcd = {}
	if hist_date_time_flag:
		tmstmp = formatLTime(endianess, tm_format, data[0:LTIME_LENGTH.get(tm_format)])
		if tmstmp:
			rcd['Time'] = tmstmp
		data = data[LTIME_LENGTH.get(tm_format):]
	if event_number_flag:
		rcd['Event Number'] = unpack(endianess + 'H', data[:2])[0]
		data = data[2:]
	if hist_seq_nbr_flag:
		rcd['History Sequence Number'] = unpack(endianess + 'H', data[:2])[0]
		data = data[2:]
	rcd['User ID'] = unpack(endianess + 'H', data[:2])[0]
	rcd['Procedure Number'], rcd['Std vs Mfg'] = getTableIDBBFLD(endianess, data[2:4])
	rcd['Arguments'] = data[4:]
	return rcd

def getTableIDBBFLD(endianess, data):
	"""
	Return data from a packed TABLE_IDB_BFLD bit-field.
	
	@type endianess: String ('>' or '<')
	@param endianess: The endianess to use when packing values
	
	@type data: String
	@param data: The packed and machine-formatted data to parse
	
	@rtype: Tuple (proc_nbr, std_vs_mfg)
	"""
	bfld = unpack(endianess + 'H', data[:2])[0]
	proc_nbr = bfld & 2047
	std_vs_mfg = bool(bfld & 2048)
	return (proc_nbr, std_vs_mfg)

def getTableIDCBFLD(endianess, data):
	"""
	Return data from a packed TABLE_IDC_BFLD bit-field.
	
	@type endianess: String ('>' or '<')
	@param endianess: The endianess to use when packing values
	
	@type data: String
	@param data: The packed and machine-formatted data to parse
	
	@rtype: Tuple (proc_nbr, std_vs_mfg, proc_flag, flag1, flag2, flag3)
	"""
	bfld = unpack(endianess + 'H', data[:2])[0]
	proc_nbr = bfld & 2047
	std_vs_mfg = bool(bfld & 2048)
	proc_flag = bool(bfld & 4096)
	flag1 = bool(bfld & 8192)
	flag2 = bool(bfld & 16384)
	flag3 = bool(bfld & 32768)
	return (proc_nbr, std_vs_mfg, proc_flag, flag1, flag2, flag3)

class C1219ProcedureInit:
	"""
	A C1219 Procedure Request, this data is written to table 7 in order to
	start a procedure.
	
	@type endianess: String ('>' or '<')
	@param endianess: The endianess to use when packing values
	
	@type table_proc_nbr: Integer (0 <= table_proc_nbr <= 2047)
	@param table_proc_nbr: The numeric procedure identifier.
	
	@type std_vs_mfg: Boolean
	@param std_vs_mfg: Wheter the procedure is manufacturer specified
	or not.  True is manufacturer specified.
	
	@type selector: Integer (0 <= selector <= 15)
	@param selector: Controls how data is returned.
		0: Post response in PROC_RESPONSE_TBL (#8) on completion.
		1: Post response in PROC_RESPONSE_TBL (#8) on exception.
		2: Do not post response in PROC_RESPONSE_TBL (#8).
		3: Post response in PROC_RESPONSE_TBL (#8) immediately and another
			response in PROC_RESPONSE_TBL (#8) on completion.
		4-15: Reserved.
	
	@type seqnum: Integer (0x00 <= seqnum <= 0xff)
	@param seqnum: The identifier for this procedure to be used for
	coordination.
	
	@type params: String
	@param params: The parameters to pass to the procedure initiation
	request.
	"""
	def __init__(self, endianess, table_proc_nbr, std_vs_mfg, selector, seqnum, params = ''):
		mfg_defined = 0
		if std_vs_mfg:
			mfg_defined = 1
		mfg_defined = mfg_defined << 11
		selector = selector << 4
		
		self.table_idb_bfld = pack(endianess + 'H', (table_proc_nbr | mfg_defined | selector))
		self.seqnum = chr(seqnum)
		self.params = params
	
	def __str__(self):
		return self.table_idb_bfld + self.seqnum + self.params
