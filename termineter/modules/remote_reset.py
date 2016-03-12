#  termineter/modules/remote_reset.py
#
#  Copyright 2012 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
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

import struct

from c1218.errors import C1218ReadTableError, C1218WriteTableError
from c1219.errors import C1219ProcedureError
from termineter.templates import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = ['Spencer McIntyre']
		self.description = 'Initiate A Reset Procedure'
		self.detailed_description = 'Initiate a remote reset procedure. Despite the name, this module is used locally through the optical interface.'
		self.options.add_boolean('DEMAND', 'perform a demand reset', default=False)
		self.options.add_boolean('SELFREAD', 'perform a self read', default=False)

	def run(self):
		conn = self.frmwk.serial_connection

		params = 0
		if self.options['DEMAND']:
			params |= 0b01
		if self.options['SELFREAD']:
			params |= 0b10

		self.frmwk.print_status('Initiating Reset Procedure')

		try:
			conn.run_procedure(9, False, struct.pack('B', params))
		except (C1218ReadTableError, C1218WriteTableError, C1219ProcedureError) as error:
			self.frmwk.print_exception(error)
		else:
			self.frmwk.print_good('Successfully Reset The Meter')
