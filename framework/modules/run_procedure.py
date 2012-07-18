#  framework/modules/run_procedure.py
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
from binascii import unhexlify
from c1219.constants import C1219_PROC_RESULT_CODES

class Module(module_template):
	def __init__(self, *args, **kwargs):
		module_template.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Initiate A Custom Procedure'
		self.detailed_description = 'This module executes a user defined procedure and returns the response. This is achieved by writing to the Procedure Initiate Table (#7) and then reading the result from the Procedure Response Table (#8).'
		self.options.addInteger('PROCNBR', 'procedure number to execute')
		self.options.addString('PARAMS', 'parameters to pass to the executed procedure', default = '')
		self.options.addBoolean('USEHEX', 'specifies that the \'PARAMS\' option is represented in hex', default = True)
		self.advanced_options.addBoolean('STDVSMFG', 'if true, specifies that this procedure is defined by the manufacturer', default = False)
	
	def run(self, frmwk, args):
		logger = frmwk.get_module_logger(self.name)
		if not frmwk.serial_login():	# don't alert on failed logins
			logger.warning('meter login failed')
			frmwk.print_error('Meter login failed, can not execute procedure')
			return
		
		data = self.options['PARAMS']
		if self.options['USEHEX']:
			data = unhexlify(data)
		
		conn = frmwk.serial_connection
		errCode, data = conn.runProcedure(self.options['PROCNBR'], self.advanced_options['STDVSMFG'], data)
		conn.stop()
		
		frmwk.print_status('Finished running procedure #' + str(self.options['PROCNBR']))
		frmwk.print_status('Received respose from procedure: ' + (C1219_PROC_RESULT_CODES.get(errCode) or 'UNKNOWN'))
		if len(data):
			frmwk.print_status('Received data output from procedure: ')
			frmwk.print_hexdump(data)
		return
