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

class Module(module_template):
	def __init__(self):
		module_template.__init__(self)
		self.version = 1
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Get Basic Meter Information By Reading Tables'
		self.detailed_description = 'This module retreives some basic meter information and displays it in a human-readable way.'
	
	def run(self, frmwk, args):
		logger = frmwk.get_module_logger(self.name)
		if not frmwk.serial_login():	# don't alert on failed logins
			logger.warning('meter login failed')
		conn = frmwk.serial_connection
		meter_info = {}
		try:
			meter_info = conn.getMeterInfo()
		except C1218ReadTableError as error:
			logger.error('caught C1218ReadTableError: ' + str(error))
			frmwk.print_error('Caught C1218ReadTableError: ' + str(error))
		conn.stop()
		for name, value in meter_info.iteritems():
			frmwk.print_status(name + ' = ' + value)
		return
