#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/run_procedure.py
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the project nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from __future__ import unicode_literals

import binascii
import re

from c1219.constants import C1219_PROCEDURE_NAMES, C1219_PROC_RESULT_CODES
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Initiate A Custom Procedure'
		self.detailed_description = 'This module executes a user defined procedure and returns the response. This is achieved by writing to the Procedure Initiate Table (#7) and then reading the result from the Procedure Response Table (#8).'
		self.options.add_integer('PROC_NUMBER', 'procedure number to execute')
		self.options.add_string('PARAMS', 'parameters to pass to the executed procedure', default='')
		self.options.add_boolean('USE_HEX', 'specifies that the \'PARAMS\' option is represented in hex', default=True)
		self.advanced_options.add_boolean('STD_VS_MFG', 'if true, specifies that this procedure is defined by the manufacturer', default=False)

	def run(self):
		conn = self.frmwk.serial_connection

		data = self.options['PARAMS']
		if self.options['USE_HEX']:
			data = data.replace(' ', '')
			hex_regex = re.compile('^([0-9a-fA-F]{2})+$')
			if hex_regex.match(data) is None:
				self.frmwk.print_error('Non-hex characters found in \'PARAMS\'')
				return
			data = binascii.a2b_hex(data)
		else:
			data = data.encode('utf-8')

		self.frmwk.print_status('Initiating procedure ' + (C1219_PROCEDURE_NAMES.get(self.options['PROC_NUMBER']) or '#' + str(self.options['PROC_NUMBER'])))

		error_code, data = conn.run_procedure(self.options['PROC_NUMBER'], self.advanced_options['STD_VS_MFG'], data)

		self.frmwk.print_status('Finished running procedure #' + str(self.options['PROC_NUMBER']))
		self.frmwk.print_status('Received response from procedure: ' + (C1219_PROC_RESULT_CODES.get(error_code) or 'UNKNOWN'))
		if len(data):
			self.frmwk.print_status('Received data output from procedure: ')
			self.frmwk.print_hexdump(data)
