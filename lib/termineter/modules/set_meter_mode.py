#  termineter/modules/set_meter_mode.py
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

import struct

from c1218.errors import C1218ReadTableError, C1218WriteTableError
from c1219.constants import C1219_METER_MODE_NAMES, C1219_PROC_RESULT_CODES
from c1219.errors import C1219ProcedureError
from termineter.templates import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = ['Spencer McIntyre']
		self.description = 'Change the Meter\'s Operating Mode'
		self.detailed_description = 'Change the operating mode of the meter. Accepted values for MODE are METERING, TEST, METERSHOP, and FACTORY.'
		self.options.add_string('MODE', 'the mode to set the meter to', True)

	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		mode = self.options['MODE']
		mode = mode.upper()
		mode = mode.replace('_', '')
		mode = mode.replace(' ', '')
		if mode[-4:] == 'MODE':
			mode = mode[:-4]
		mode_dict = C1219_METER_MODE_NAMES
		if not mode in mode_dict:
			self.frmwk.print_error('unknown mode, please use METERING, TEST, METERSHOP, or FACTORY')
			return

		logger.info('setting mode to: ' + mode)
		self.frmwk.print_status('Setting Mode To: ' + mode)

		mode = mode_dict[mode]
		try:
			result_code, response_data = conn.run_procedure(6, False, struct.pack('B', mode))
		except C1218ReadTableError as error:
			self.frmwk.print_exception(error)
			return
		except C1218WriteTableError as error:
			if error.code == 4:  # onp/operation not possible
				self.frmwk.print_error('Meter responded that it can not set the mode to the desired type')
			else:
				self.frmwk.print_exception(error)
			return
		except C1219ProcedureError as error:
			self.frmwk.print_exception(error)
			return

		if result_code < 2:
			self.frmwk.print_good(C1219_PROC_RESULT_CODES[result_code])
		else:
			self.frmwk.print_error(C1219_PROC_RESULT_CODES.get(result_code, "Unknown status code: {0}".format(result_code)))
