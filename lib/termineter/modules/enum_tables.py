#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/enum_tables.py
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

from time import sleep

from c1218.errors import C1218ReadTableError
from c1219.data import C1219_TABLES
from termineter.module import TermineterModuleOptical

# 0     - 2039  Standard Tables
# 2048  - 4087  Manufacturer Tables 0 - 2039
# 4096  - 6135  Standard Pending Tables 0 - 2039
# 6144  - 8183  Manufacturer Pending Tables 0 - 2039
# 8192  - 10231 User Defined Tables 0 - 2039
# 12288 - 14327 User Defined Pending Tables 0 - 2039
class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Enumerate Readable C12.19 Tables From The Device'
		self.detailed_description = """\
		This module will enumerate the readable tables on the smart meter by attempting to transfer each one. Tables are
		grouped into decades.
		"""
		self.options.add_integer('LOWER', 'table id to start reading from', default=0)
		self.options.add_integer('UPPER', 'table id to stop reading from', default=256)

	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		lower_boundary = self.options['LOWER']
		upper_boundary = self.options['UPPER']

		number_of_tables = 0
		self.frmwk.print_status('Enumerating tables, please wait...')
		for table_id in range(lower_boundary, (upper_boundary + 1)):
			try:
				conn.get_table_data(table_id)
			except C1218ReadTableError:
				self.frmwk.serial_disconnect()
				logger.warning('received ISSS error, connection stopped, will sleep before retrying')
				sleep(0.5)
				self.frmwk.serial_connect()
				if not self.frmwk.serial_login():
					logger.warning('meter login failed, some tables may not be accessible')
				conn = self.frmwk.serial_connection
			else:
				self.frmwk.print_status('Found readable table, ID: ' + str(table_id) + ' Name: ' + (C1219_TABLES.get(table_id) or 'UNKNOWN'))
				number_of_tables += 1
		self.frmwk.print_status("Found {0:,} tables in range {1}-{2}.".format(number_of_tables, lower_boundary, upper_boundary))
