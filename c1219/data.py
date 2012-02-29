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

from struct import pack, unpack

C1219_TABLES = {
	0: 'General Configuration Table',
	1: 'General Manufacturer Identification Table',
	2: 'Device Nameplate Table',
	3: 'ED_MODE Status Table',
	4: 'Pending Status Table',
	5: 'Device Identification Table',
	6: 'Utility Information Table',
	7: 'Procedure Initiate Table',
	8: 'Procedure Response Table',
	10: 'Dimension Sources Limiting Table',
	11: 'Actual Sources Limiting Table',
	12: 'Unit of Measure Entry Table',
	13: 'Demand Control Table',
	14: 'Data Control Table',
	15: 'Constants Table',
	16: 'Source Definition Table',
	17: 'Transformer Loss Compensation Table',
	20: 'Dimension Register Table',
	21: 'Actual Register Table',
	22: 'Data Selection Table',
	23: 'Current Register Data Table',
	24: 'Previous Season Data Table',
	25: 'Previous Demand Reset Data Table',
	26: 'Self Read Data Table',
	27: 'Present Register Selection Table',
	28: 'Present Register Data Table',
	30: 'Dimension Display Table', 
	31: 'Actual Display Table',
	32: 'Display Source Table',
	33: 'Primary Display List Table',
	34: 'Secondary Display List Table',
	40: 'Dimension Security Limiting Table',
	41: 'Actual Security Limiting Table',
	42: 'Security Table',
	43: 'Default Access Control Table',
	44: 'Access Control Table',
	45: 'Key Table',
	50: 'Dimension Time and TOU Table',
	51: 'Actual Time and TOU Table',
	52: 'Clock Table',
	53: 'Time Offset Table',
	54: 'Calender Table',
	55: 'Clock State Table',
	56: 'Time Remaining Table',
	57: 'Precision Clock State Table',
	60: 'Dimension Load Profile Table',
	61: 'Actual Load Profile Table',
	62: 'Load Profile Control Table',
	63: 'Load Profile Status Table',
	64: 'Load Profile Data Set 1 Table',
	65: 'Load Profile Data Set 2 Table',
	66: 'Load Profile Data Set 3 Table',
	67: 'Load Profile Data Set 4 Table',
	70: 'Dimension Log Table',
	71: 'Actual Log Table',
	72: 'Events Identification Table',
	73: 'History Log Control Table',
	74: 'History Log Data Table',
	75: 'Event Log Control Table',
	76: 'Event Log Data Table',
	77: 'Event Log and Signatures Enable Table',
	78: 'End Device Program State Table',
	79: 'Event Counters Table',
	80: 'Dimension User Defined Tables Function Limiting Table',
	81: 'Actual User Defined Tables Function Limiting Table',
	82: 'User Defined Tables List Table',
	83: 'User Defined Tables Selection Table',
	84: 'User Defined Table 0 Table',
	85: 'User Defined Table 1 Table',
	86: 'User Defined Table 2 Table',
	87: 'User Defined Table 3 Table',
	88: 'User Defined Table 4 Table',
	89: 'User Defined Table 5 Table',
	90: 'Dimension Telephone Table',
	91: 'Actual Telephone Table',
	92: 'Global Parameters Table',
	93: 'Originate Parameters Table',
	94: 'Originate Schedule Table',
	95: 'Answer Parameters',
	96: 'Call Purpose',
	97: 'Call Status',
	98: 'Originate Status',
	100: 'Dimension Extended Source Limiting Table',
	101: 'Actual Extending Source Limiting Table',
	102: 'Source Information Table',
	103: 'External Scaling Table',
	104: 'Demand Control Table',
	105: 'Transformer Loss Compensation',
	106: 'Gas Constant AGA3',
	107: 'Gas Constant AGA7',
	110: 'Dimension Load Control',
	111: 'Actual Load Control Limiting Table',
	112: 'Load Control Status',
	113: 'Load Control Configuration',
	114: 'Load Control Schedule',
	115: 'Load Control Conditions',
	116: 'Prepayment Status',
	117: 'Prepayment Control',
	118: 'Billing Control',
	140: 'Extended User-defined Tables Function Limiting Table',
	141: 'Extended User-defined Tables Actual Limits Table',
	142: 'Extended User-defined Selections Table',
	143: 'Extended User-defined Constants Table',
	150: 'Quality of Service Dimension Limits Table',
	151: 'Actual Quality of Service Limiting Table',
	152: 'Quality of Service Control Table',
	153: 'Quality of Service Incidents Table',
	154: 'Quality of Servce Log Table',
	155: 'Asynchronous Time-Domain Waveforms Table',
	156: 'Asynchronous Frequency-Domain Spectrum Table',
	157: 'Periodic Time Domain Waveforms Table',
	158: 'Periodic Frequency-Domain Spectrum Table',
	160: 'Dimension One-Way',
	161: 'Actual One-Way',
	162: 'One-Way Control Table',
	163: 'One-Way Data Table',
	164: 'One-Way Commands/Responses/Extended User-defined Tables Table',
}

class c1219ProcedureInit:
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
