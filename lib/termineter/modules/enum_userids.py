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

from termineter.templates import TermineterModuleOptical

class Module(TermineterModuleOptical):
	require_connection = False
	attempt_login = False
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = ['Spencer McIntyre']
		self.description = 'Enumerate Valid User IDs From The Device'
		self.detailed_description = 'This module will enumerate existing user IDs from the device.'
		self.options.add_string('USERNAME', 'user name to attempt to log in as', default='0000')
		self.options.add_integer('LOWER', 'user id to start enumerating from', default=0)
		self.options.add_integer('UPPER', 'user id to stop enumerating from', default=50)
		self.advanced_options.add_float('DELAY', 'time in seconds to wait between attempts', default=0.20)

	def run(self):
		conn = self.frmwk.serial_connection
		lower_boundary = self.options['LOWER']
		upper_boundary = self.options['UPPER']
		if lower_boundary > 0xffff:
			self.frmwk.print_error('LOWER option set to high (exceeds 0xffff)')
			return
		if upper_boundary > 0xffff:
			self.frmwk.print_error('UPPER option set to high (exceeds 0xffff)')
			return
		time_delay = self.advanced_options['DELAY']

		self.frmwk.print_status('Enumerating user IDs, please wait...')
		for user_id in range(lower_boundary, (upper_boundary + 1)):
			while not conn.start():
				sleep(time_delay)
			if conn.login(self.options['USERNAME'], user_id):
				self.frmwk.print_good('Found a valid User ID: ' + str(user_id))
			while not conn.stop(force=True):
				sleep(time_delay)
			sleep(time_delay)
		return
