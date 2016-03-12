#  termineter/modules/get_info.py
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

from c1218.errors import C1218ReadTableError
from c1219.access.general import C1219GeneralAccess
from termineter.templates import TermineterModuleOptical

STATUS_FLAGS = flags = (
	'Unprogrammed',
	'Configuration Error',
	'Self Check Error',
	'RAM Failure',
	'ROM Failure',
	'Non Volatile Memory Failure',
	'Clock Error',
	'Measurement Error',
	'Low Battery',
	'Low Loss Potential',
	'Demand Overload',
	'Power Failure',
	'Tamper Detect',
	'Reverse Rotation'
)

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = ['Spencer McIntyre']
		self.description = 'Get Basic Meter Information By Reading Tables'
		self.detailed_description = 'This module retreives some basic meter information and displays it in a human-readable way.'

	def run(self):
		conn = self.frmwk.serial_connection

		try:
			general_ctl = C1219GeneralAccess(conn)
		except C1218ReadTableError:
			self.frmwk.print_error('Could not read the necessary tables')
			return

		meter_info = {}
		meter_info['Character Encoding'] = general_ctl.char_format
		meter_info['Device Type'] = general_ctl.nameplate_type
		meter_info['C12.19 Version'] = {0: 'Pre-release', 1: 'C12.19-1997', 2: 'C12.19-2008'}.get(general_ctl.std_version_no) or 'Unknown'
		meter_info['Manufacturer'] = general_ctl.manufacturer
		meter_info['Model'] = general_ctl.ed_model
		meter_info['Hardware Version'] = str(general_ctl.hw_version_no) + '.' + str(general_ctl.hw_revision_no)
		meter_info['Firmware Version'] = str(general_ctl.fw_version_no) + '.' + str(general_ctl.fw_revision_no)
		meter_info['Serial Number'] = general_ctl.mfg_serial_no

		if general_ctl.ed_mode is not None:
			modes = []
			flags = ['Metering', 'Test Mode', 'Meter Shop Mode', 'Factory']
			for i in range(len(flags)):
				if general_ctl.ed_mode & (2 ** i):
					modes.append(flags[i])
			if len(modes):
				meter_info['Mode Flags'] = ', '.join(modes)

		if general_ctl.std_status is not None:
			status = []
			for i, flag in enumerate(STATUS_FLAGS):
				if general_ctl.std_status & (2 ** i):
					status.append(flag)
			if len(status):
				meter_info['Status Flags'] = ', '.join(status)
		if general_ctl.device_id is not None:
			meter_info['Device ID'] = general_ctl.device_id

		self.frmwk.print_status('General Information:')
		fmt_string = "    {0:.<38}.{1}"
		keys = sorted(list(meter_info.keys()))
		for key in keys:
			self.frmwk.print_status(fmt_string.format(key, meter_info[key]))
