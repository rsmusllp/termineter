#  framework/modules/dump_tables.py
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

import os
from time import sleep

from c1218.errors import C1218ReadTableError
from c1219.data import C1219_TABLES
from framework.templates import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 2
		self.author = ['Spencer McIntyre']
		self.description = 'Dump Readable C12.19 Tables From The Device To A CSV File'
		self.detailed_description = 'This module will enumerate the readable tables on the smart meter and write them out to a CSV formated file for analysis. The format is table id, table name, table data length, table data.  The table data is represented in hex.'
		self.options.add_integer('LOWER', 'table id to start reading from', default=0)
		self.options.add_integer('UPPER', 'table id to stop reading from', default=256)
		self.options.add_string('FILE', 'file to write the csv data into', default='smart_meter_tables.csv')

	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		lower_boundary = self.options['LOWER']
		upper_boundary = self.options['UPPER']
		out_file = open(self.options['FILE'], 'w', 1)
		if not self.frmwk.serial_login():
			logger.warning('meter login failed, some tables may not be accessible')

		number_of_tables = 0
		self.frmwk.print_status('Starting Dump. Writing table data to: ' + self.options.get_option_value('FILE'))
		for tableid in xrange(lower_boundary, (upper_boundary + 1)):
			try:
				data = conn.get_table_data(tableid)
			except C1218ReadTableError as error:
				data = None
				if error.code == 10:	# ISSS
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
							raise error	# tried to re-sync communications but failed, you should reconnect and rerun the module
			if data:
				self.frmwk.print_status('Found readable table, ID: ' + str(tableid) + ' Name: ' + (C1219_TABLES.get(tableid) or 'UNKNOWN'))
				# format is: table id, table name, table data length, table data
				out_file.write(','.join([str(tableid), (C1219_TABLES.get(tableid) or 'UNKNOWN'), str(len(data)), data.encode('hex')]) + os.linesep)
				number_of_tables += 1

		out_file.close()
		self.frmwk.print_status('Successfully copied ' + str(number_of_tables) + ' tables to disk.')
		return
