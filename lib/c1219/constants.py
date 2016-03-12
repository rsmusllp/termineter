#  c1219/constants.py
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

from __future__ import unicode_literals

GEN_CONFIG_TBL = 0
GENERAL_MFG_ID_TBL = 1
ED_MODE_STATUS_TBL = 3
DEVICE_IDENT_TBL = 5
PROC_INITIATE_TBL = 7
PROC_RESPONSE_TBL = 8
DIM_REGS_TBL = 20
ACT_REGS_TBL = 21
DATA_SELECTION_TBL = 22
CURRENT_REG_DATA_TBL = 23
PREVIOUS_SEASON_DATA_TBL = 24
PREVIOUS_DEMAND_RESET_DATA_TBL = 25
SELF_READ_DATA_TBL = 26
PRESENT_REGISTER_SELECT_TBL = 27
PRESENT_REGISTER_DATA_TBL = 28
DIM_DISP_TBL = 30
ACT_DISP_TBL = 31
DISP_SOURCE_TBL = 32
PRI_DISP_LIST_TBL = 33
SEC_DISP_LIST_TBL = 34
DIM_SECURITY_LIMITING_TBL = 40
ACT_SECURITY_LIMITING_TBL = 41
SECURITY_TBL = 42
DEFAULT_ACCESS_CONTROL_TBL = 43
ACCESS_CONTROL_TBL = 44
KEY_TBL = 45
ACT_LOG_TBL = 71
HISTORY_LOG_DATA_TBL = 74
ACT_TELEPHONE_TBL = 91
GLOBAL_PARAMETERS_TBL = 92
ORIGINATE_PARAMETERS_TBL = 93
ORIGINATE_SCHEDULE_TBL = 94
ANSWER_PARAMETERS_TBL = 95
CALL_PURPOSE_TBL = 96
CALL_STATUS_TBL = 97
ORIGINATE_STATUS_TBL = 98

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
	30: 'Dimension Display Limits Table',
	31: 'Actual Display Limiting Table',
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

C1219_EVENT_CODES = {
	0: 'No Event',
	1: 'Primary Power Down',
	2: 'Primary Power Up',
	3: 'Time Changed (Time-stamp is old time)',
	4: 'Time Changed (Time-stamp is new time)',
	5: 'Time Changed (Time-stamp is old time in STIME_DATE format)',
	6: 'Time Changed (Time-stamp new time in STIME_DATE format)',
	7: 'End Device Accessed for Read',
	8: 'End Device Accessed for Write',
	9: 'Procedure Invoked',
	10: 'Table Written To',
	11: 'End Device Programmed',
	12: 'Communication Terminated Normally',
	13: 'Communication Terminated Abnormally',
	14: 'Reset List Pointers',
	15: 'Updated List Pointers',
	16: 'History Log Cleared',
	17: 'History Log Pointers Updated',
	18: 'Event Log Cleared',
	19: 'Event Log Pointers Updated',
	20: 'Demand Reset Occurred',
	21: 'Self Read Occurred',
	22: 'Daylight Saving Time On',
	23: 'Daylight Savings Time Off',
	24: 'Season Changed',
	25: 'Rate Change',
	26: 'Special Schedule Activated',
	27: 'Tier Switch / Change',
	28: 'Pending Table Activated',
	29: 'Pending Table Activation Cleared',
	30: 'Metering mode started',
	31: 'Metering mode stopped',
	32: 'Test mode started',
	33: 'Test mode stopped',
	34: 'Meter shop mode started',
	35: 'Meter shop mode stopped',
	36: 'End Device reprogrammed',
	37: 'Configuration error detected',
	38: 'Self check error detected',
	39: 'RAM failure detected',
	40: 'ROM failure detected',
	41: 'Nonvolatile memory failure detected',
	42: 'Clock error detected',
	43: 'Measurement error detected',
	44: 'Low battery detected',
	45: 'Low loss potential detected',
	46: 'Demand overload detected',
	47: 'Tamper attempt detected',
	48: 'Reverse rotation detected',
	49: 'Control point changed by a command',
	50: 'Control point changed by the schedule',
	51: 'Control point changed by a condition',
	52: 'Control point changed for the prepayment',
	53: 'Added to remaining credit',
	54: 'Subtracted from remaining credit',
	55: 'Adjusted the remaining credit',
	56: 'End Device sealed',
	57: 'End Device unsealed',
	58: 'Procedure Invoked (with values)',
	59: 'Table Written To (with values)',
	60: 'End Device Programmed (with values)',
	61: 'End Device sealed (with values)',
	62: 'End Device unsealed (with values)',
	63: 'Procedure Invoked (with signature)',
	64: 'Table Written To (with signature)',
	65: 'End Device Programmed (with signature)',
	66: 'End Device sealed (with signature)',
	67: 'End Device unsealed (with signature)',
	68: 'Procedure Invoked (with signature and values)',
	69: 'Table Written To(with signature and values)',
	70: 'End Device Programmed (with signature and values)',
	71: 'End Device sealed(with signature and values)',
	72: 'End Device unsealed(with signature and values)',
	73: 'Read Secured Table',
	74: 'Read Secured Register',
	75: 'Read Secured Table (with values)',
	76: 'Read Secured Register (with values)'
}

C1219_PROCEDURE_NAMES = {
	0: 'Cold Start',
	1: 'Warm Start',
	2: 'Save Configuration',
	3: 'Clear Data',
	4: 'Reset List Pointers',
	5: 'Update Last Read Entry',
	6: 'Change End Device Mode',
	7: 'Clear Standard Status Flags',
	8: 'Clear Manufacturer Flags',
	9: 'Remote Reset',
	10: 'Set Date and/or Time',
	11: 'Execute Diagnostics Procedure',
	12: 'Activate All Pending Tables',
	13: 'Activate Specific Pending Table(s)',
	14: 'Clear All Pending Tables',
	15: 'Clear Specific Pending Table(s)',
	16: 'Start Load Profile',
	17: 'Stop Load Profile',
	18: 'Log In',
	19: 'Log Out',
	20: 'Initiate an Immediate Call',
	21: 'Direct Load Control',
	22: 'Modify Credit',
	27: 'Clear Pending Call Status',
	28: 'Start Quality of Service Monitors',
	29: 'Stop Quality of Service Monitors',
	30: 'Start Secured Registers',
	31: 'Stop Secured Registers',
	32: 'Set Precision Date and/or Time'
}

C1219_PROC_RESULT_CODES = {
	0: 'Procedure completed',
	1: 'Procedure accepted but not fully completed',
	2: 'Invalid parameter for known procedure, procedure was ignored',
	3: 'Procedure conflicts with current device setup, procedure was ignored',
	4: 'Timing constraint, procedure was ignored',
	5: 'No authorization for requested procedure, procedure was ignored',
	6: 'Unrecognized procedure, procedure was ignored'
}

C1219_CALL_STATUS_FLAGS = {
	0:  'No phone call made',
	1:  'Phone call in progress',
	2:  'Dialing',
	3:  'Waiting for a connection',
	4:  'Communicating',
	5:  'Completed normally',
	6:  'Not completed',
	7:  'Not completed, Line busy',
	8:  'Not completed, No dial tone',
	9:  'Not completed, Line cut',
	10: 'Not completed, No Connection',
	11: 'Not completed, No modem response'
}

C1219_METER_MODE_FLAGS = {
	1: 'METERING',
	2: 'TEST',
	4: 'METERSHOP',
	8: 'FACTORY'
}

C1219_METER_MODE_NAMES = {
	'METERING':  1,
	'TEST':      2,
	'METERSHOP': 4,
	'FACTORY':   8
}

LTIME_LENGTH = {0: 0, 1: 6, 2: 6, 3: 5, 4: 4}
MONTHS = {
	1:  'JAN',
	2:  'FEB',
	3:  'MAR',
	4:  'APR',
	5:  'MAY',
	6:  'JUN',
	7:  'JUL',
	8:  'AUG',
	9:  'SEP',
	10: 'OCT',
	11: 'NOV',
	12: 'DEC'
}
