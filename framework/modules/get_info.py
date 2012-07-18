#  framework/modules/get_info.py
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

from framework.templates import module_template
from c1218.errors import C1218ReadTableError
from c1219.access.general import C1219GeneralAccess

class Module(module_template):
	def __init__(self, *args, **kwargs):
		module_template.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Get Basic Meter Information By Reading Tables'
		self.detailed_description = 'This module retreives some basic meter information and displays it in a human-readable way.'
	
	def run(self, frmwk, args):
		logger = frmwk.get_module_logger(self.name)
		if not frmwk.serial_login():	# don't alert on failed logins
			logger.warning('meter login failed, not all information may be available')
			frmwk.print_error('Meter login failed, not all information may be available')
		conn = frmwk.serial_connection
		
		try:
			generalCtl = C1219GeneralAccess(conn)
		except C1218ReadTableError:
			frmwk.print_error('Could not read the necessary tables')
			return
		conn.stop()
		
		meter_info = {}
		meter_info['Character Encoding'] = generalCtl.char_format
		meter_info['Device Type'] = generalCtl.nameplate_type
		meter_info['C12.19 Version'] =  {0:'Pre-release', 1:'C12.19-1997', 2:'C12.19-2008'}.get(generalCtl.std_version_no) or 'Unknown'
		meter_info['Manufacturer'] = generalCtl.manufacturer
		meter_info['Model'] = generalCtl.ed_model
		meter_info['Hardware Version'] = str(generalCtl.hw_version_no) + '.' + str(generalCtl.hw_revision_no)
		meter_info['Firmware Version'] = str(generalCtl.fw_version_no) + '.' + str(generalCtl.fw_revision_no)
		meter_info['Serial Number'] = generalCtl.mfg_serial_no
		
		if generalCtl.ed_mode != None:
			modes = []
			flags = ['Metering', 'Test Mode', 'Meter Shop Mode', 'Factory']
			for i in range(len(flags)):
				if generalCtl.ed_mode & (2 ** i):
					modes.append(flags[i])
			if len(modes):
				meter_info['Mode Flags'] = ', '.join(modes)
		
		if generalCtl.std_status != None:
			status = []
			flags = ['Unprogrammed', 'Configuration Error', 'Self Check Error', 'RAM Failure', 'ROM Failure', 'Non Volatile Memory Failure', 'Clock Error', 'Measurement Error', 'Low Battery', 'Low Loss Potential', 'Demand Overload', 'Power Failure', 'Tamper Detect', 'Reverse Rotation']
			for i in range(len(flags)):
				if generalCtl.std_status & (2 ** i):
					status.append(flags[i])
			if len(status):
				meter_info['Status Flags'] = ', '.join(status)
		if generalCtl.device_id != None:
			meter_info['Device ID'] = generalCtl.device_id
		
		frmwk.print_status('General Information:')
		fmt_string = "    {0:.<38}.{1}"
		keys = meter_info.keys()
		keys.sort()
		for key in keys:
			frmwk.print_status(fmt_string.format(key, meter_info[key]))
		return
