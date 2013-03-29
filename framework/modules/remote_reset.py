#  framework/modules/remote_reset.py
#  
#  Copyright 2012 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
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

from framework.templates import optical_module_template
from c1219.errors import C1219ProcedureError
from c1218.errors import C1218ReadTableError, C1218WriteTableError

class Module(optical_module_template):
	def __init__(self, *args, **kwargs):
		optical_module_template.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Initiate A Reset Procedure'
		self.detailed_description = 'Initiate a remote reset procedure. Despite the name, this module is used locally through the optical interface.'
		self.options.addBoolean('DEMAND', 'perform a demand reset', default = False)
		self.options.addBoolean('SELFREAD', 'perform a self read', default = False)
	
	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		if not self.frmwk.serial_login():
			self.logger.warning('meter login failed')
			self.frmwk.print_error('Meter login failed, procedure may fail')
		
		params = 0
		if self.options['DEMAND']:
			params = (params | 0b01)
		if self.options['SELFREAD']:
			params = (params | 0b10)
		
		self.frmwk.print_status('Initiating Reset Procedure')
		
		conn = self.frmwk.serial_connection
		errCode, data = None, ''
		try:
			errCode, data = conn.run_procedure(9, False, chr(params))
			self.frmwk.print_good('Sucessfully Reset The Meter')
		except (C1218ReadTableError, C1218WriteTableError, C1219ProcedureError) as error:
			self.logger.error('caught ' + error.__class__.__name__ + ': ' + str(error))
			self.frmwk.print_error('Caught ' + error.__class__.__name__ + ': ' + str(error))
		conn.stop()
		return
