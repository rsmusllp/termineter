#  termineter/modules/set_meter_id.py
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

from c1219.access.general import C1219GeneralAccess
from termineter.templates import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = ['Spencer McIntyre']
		self.description = 'Set The Meter\'s I.D.'
		self.detailed_description = 'This module will over write the Smart Meter\'s device ID with the new value specified in METERID.'
		self.options.add_string('METERID', 'value to set the meter id to', True)

	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		meter_id = self.options['METERID']

		gen_ctl = C1219GeneralAccess(conn)
		if gen_ctl.id_form == 0:
			logger.info('device id stored in 20 byte string')
			if len(meter_id) > 20:
				self.frmwk.print_error('METERID length exceeds the allowed 20 bytes')
				return
		else:
			logger.info('device id stored in BCD(10)')
			if len(meter_id) > 10:
				self.frmwk.print_error('METERID length exceeds the allowed 10 bytes')
				return
		if gen_ctl.set_device_id(meter_id):
			self.frmwk.print_error('Could not set the Meter\'s ID')
		else:
			self.frmwk.print_status('Successfully updated the Meter\'s ID to: ' + meter_id)
