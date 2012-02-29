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

class Module(module_template):
	def __init__(self):
		module_template.__init__(self)
		self.version = 1
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Set The Meter\'s I.D.'
		self.detailed_description = 'This module will over write the Smart Meter\'s device ID with the new value specified in METERID.'
		self.options.addString('METERID', 'value to set the meter id to', True)
	
	def run(self, frmwk, args):
		meterid = self.options.getOptionValue('METERID')
		logger = frmwk.get_module_logger(self.name)
		if not frmwk.serial_login():
			logger.warning('meter login failed')
		conn = frmwk.serial_connection
		errCode = conn.setMeterID(meterid)
		conn.stop()
		
		if errCode == 0:
			frmwk.print_good('Device ID Successfully Set To: ' + meterid)
		else:
			frmwk.print_error('There was an error while trying to set the id')
		return
