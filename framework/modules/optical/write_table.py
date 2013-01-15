#  framework/modules/write_table.py
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

import re
from binascii import unhexlify
from framework.templates import optical_module_template
from c1218.errors import C1218WriteTableError

class Module(optical_module_template):
	def __init__(self, *args, **kwargs):
		optical_module_template.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Write Data To A C12.19 Table'
		self.detailed_description = 'This will over write the data in a write able table on the smart meter. If USEHEX is set to true then the DATA variable is expected to be represented as a string of hex characters.'
		self.options.addInteger('TABLEID', 'table to read from', True)
		self.options.addString('DATA', 'data to write to the table', True)
		self.options.addBoolean('USEHEX', 'specifies that the \'DATA\' option is represented in hex', default = False)
		self.options.addInteger('OFFSET', 'offset to start writing data at', required = False, default = None)
	
	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		tableid = self.options['TABLEID']
		data = self.options['DATA']
		offset = self.options['OFFSET']
		if self.options['USEHEX']:
			hex_regex = re.compile('^([0-9a-fA-F]{2})+$')
			if hex_regex.match(data) == None:
				self.frmwk.print_error('Non-hex characters found in \'DATA\'')
				return
			data = unhexlify(data)
		
		if not self.frmwk.serial_login():
			logger.warning('meter login failed')
			self.frmwk.print_error('Meter login failed')
			return
		
		try:
			conn.setTableData(tableid, data, offset)
			self.frmwk.print_status('Successfully Wrote Data')
		except C1218WriteTableError as error:
			self.frmwk.print_error('Caught C1218WriteTableError: ' + str(error))
		conn.stop()
