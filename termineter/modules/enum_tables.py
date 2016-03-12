#  termineter/modules/enum_tables.py
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

from time import sleep

from c1218.errors import C1218ReadTableError
from c1219.data import C1219_TABLES
from termineter.templates import TermineterModuleOptical

# 0     - 2039  Standard Tables
# 2048  - 4087  Manufacturer Tables 0 - 2039
# 4096  - 6135  Standard Pending Tables 0 - 2039
# 6144  - 8183  Manufacturer Pending Tables 0 - 2039
# 8192  - 10231 User Defined Tables 0 - 2039
# 12288 - 14327 User Defined Pending Tables 0 - 2039
class Module(TermineterModuleOptical):
	require_connection = False
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 4
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
		for tableid in range(lower_boundary, (upper_boundary + 1)):
			try:
				data = conn.get_table_data(tableid)
			except C1218ReadTableError as error:
				data = None
				if error.code == 10:  # ISSS
					conn.stop()
					logger.warning('received ISSS error, connection stopped, will sleep before retrying')
					sleep(0.5)
					if not self.frmwk.serial_login():
						logger.warning('meter login failed, some tables may not be accessible')
					try:
						data = conn.get_table_data(tableid)
					except C1218ReadTableError as error:
						data = None
						if error.code == 10:
							raise error  # tried to re-sync communications but failed, you should reconnect and rerun the module
			if data:
				self.frmwk.print_status('Found readable table, ID: ' + str(tableid) + ' Name: ' + (C1219_TABLES.get(tableid) or 'UNKNOWN'))
				number_of_tables += 1
		self.frmwk.print_status("Found {0:,} tables in range {1}-{2}.".format(number_of_tables, lower_boundary, upper_boundary))
