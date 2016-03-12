#  termineter/modules/run_procedure.py
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

import binascii
import re

from c1219.constants import C1219_PROCEDURE_NAMES, C1219_PROC_RESULT_CODES
from termineter.templates import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 2
		self.author = ['Spencer McIntyre']
		self.description = 'Initiate A Custom Procedure'
		self.detailed_description = 'This module executes a user defined procedure and returns the response. This is achieved by writing to the Procedure Initiate Table (#7) and then reading the result from the Procedure Response Table (#8).'
		self.options.add_integer('PROCNBR', 'procedure number to execute')
		self.options.add_string('PARAMS', 'parameters to pass to the executed procedure', default='')
		self.options.add_boolean('USEHEX', 'specifies that the \'PARAMS\' option is represented in hex', default=True)
		self.advanced_options.add_boolean('STDVSMFG', 'if true, specifies that this procedure is defined by the manufacturer', default=False)

	def run(self):
		conn = self.frmwk.serial_connection

		data = self.options['PARAMS']
		if self.options['USEHEX']:
			data = data.replace(' ', '')
			hex_regex = re.compile('^([0-9a-fA-F]{2})+$')
			if hex_regex.match(data) is None:
				self.frmwk.print_error('Non-hex characters found in \'PARAMS\'')
				return
			data = binascii.a2b_hex(data)
		else:
			data = data.encode('utf-8')

		self.frmwk.print_status('Initiating procedure ' + (C1219_PROCEDURE_NAMES.get(self.options['PROCNBR']) or '#' + str(self.options['PROCNBR'])))

		error_code, data = conn.run_procedure(self.options['PROCNBR'], self.advanced_options['STDVSMFG'], data)

		self.frmwk.print_status('Finished running procedure #' + str(self.options['PROCNBR']))
		self.frmwk.print_status('Received response from procedure: ' + (C1219_PROC_RESULT_CODES.get(error_code) or 'UNKNOWN'))
		if len(data):
			self.frmwk.print_status('Received data output from procedure: ')
			self.frmwk.print_hexdump(data)
