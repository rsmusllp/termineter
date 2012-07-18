#  framework/modules/set_meter_id.py
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
from c1219.access.general import C1219GeneralAccess

class Module(module_template):
	def __init__(self, *args, **kwargs):
		module_template.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Set The Meter\'s I.D.'
		self.detailed_description = 'This module will over write the Smart Meter\'s device ID with the new value specified in METERID.'
		self.options.addString('METERID', 'value to set the meter id to', True)
	
	def run(self, frmwk, args):
		meterid = self.options['METERID']
		logger = frmwk.get_module_logger(self.name)
		if not frmwk.serial_login():
			logger.warning('meter login failed')
		conn = frmwk.serial_connection
		genCtl = C1219GeneralAccess(conn)
		if genCtl.id_form == 0:
			logger.info('device id stored in 20 byte string')
			if len(meterid) > 20:
				frmwk.print_error('METERID length exceeds the allowed 20 bytes')
				return
		else:
			logger.info('device id stored in BCD(10)')
			if len(meterid) > 10:
				frmwk.print_error('METERID length exceeds the allowed 10 bytes')
				return
		if genCtl.set_device_id(meterid):
			frmwk.print_error('Could not set the Meter\'s ID')
		else:
			frmwk.print_status('Successfully updated the Meter\'s ID to: ' + meterid)
		conn.stop()
		return
