#  framework/modules/enum_tables.py
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

from time import sleep

from c1218.errors import C1218ReadTableError
from c1219.data import C1219_TABLES
from framework.templates import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 4
		self.author = [ 'Spencer McIntyre' ]
		self.description = 'Enumerate Readable C12.19 Tables From The Device'
		self.detailed_description = 'This module will enumerate the readable tables on the smart meter by attempting to transfer each one.'
		self.options.add_integer('LOWER', 'table id to start reading from', default = 0)
		self.options.add_integer('UPPER', 'table id to stop reading from', default = 256)

	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		lower_boundary = self.options['LOWER']
		upper_boundary = self.options['UPPER']
		if not self.frmwk.serial_login():
			logger.warning('meter login failed')

		number_of_tables = 0
		self.frmwk.print_status('Enumerating tables, please wait...')
		for tableid in xrange(lower_boundary, (upper_boundary + 1)):
			try:
				data = conn.get_table_data(tableid)
			except C1218ReadTableError as error:
				data = None
				if error.errCode == 10: # ISSS
					conn.stop()
					logger.warning('received ISSS error, connection stopped, will sleep before retrying')
					sleep(0.5)
					if not self.frmwk.serial_login():
						logger.warning('meter login failed, some tables may not be accessible')
					try:
						data = conn.get_table_data(tableid)
					except C1218ReadTableError as error:
						data = None
						if error.errCode == 10:
							raise error # tried to re-sync communications but failed, you should reconnect and rerun the module
			if data:
				self.frmwk.print_status('Found readable table, ID: ' + str(tableid) + ' Name: ' + (C1219_TABLES.get(tableid) or 'UNKNOWN'))
				number_of_tables += 1
		self.frmwk.print_status('Found ' + str(number_of_tables) + ' table(s).')
		return
