#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/write_table.py
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

from c1218.errors import C1218WriteTableError
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Write Data To A C12.19 Table'
		self.detailed_description = '''\
		This will over write the data in a write able table on the smart meter. If USE_HEX is set to true then the DATA
		option is expected to be represented as a string of hex characters.
		'''
		self.options.add_integer('TABLE_ID', 'table to read from', True)
		self.options.add_string('DATA', 'data to write to the table', True)
		self.options.add_boolean('USE_HEX', 'specifies that the \'DATA\' option is represented in hex', default=True)
		self.options.add_integer('OFFSET', 'offset to start writing data at', required=False, default=0)
		self.advanced_options.add_boolean('VERIFY', 'verify that the data was written with a read request', default=True)

	def run(self):
		conn = self.frmwk.serial_connection
		tableid = self.options['TABLE_ID']
		data = self.options['DATA']
		offset = self.options['OFFSET']
		if self.options['USE_HEX']:
			data = data.replace(' ', '')
			hex_regex = re.compile('^([0-9a-fA-F]{2})+$')
			if hex_regex.match(data) is None:
				self.frmwk.print_error('Non-hex characters found in \'DATA\'')
				return
			data = binascii.a2b_hex(data)
		else:
			data = data.encode('utf-8')

		try:
			conn.set_table_data(tableid, data, offset)
		except C1218WriteTableError as error:
			self.frmwk.print_exception(error)
		else:
			self.frmwk.print_status('Successfully Wrote Data')

		if self.advanced_options['VERIFY']:
			table = conn.get_table_data(tableid)
			if table[offset:offset + len(data)] == data:
				self.frmwk.print_status('Table Write Verification Passed')
			else:
				self.frmwk.print_error('Table Write Verification Failed')
			self.frmwk.print_hexdump(table)
