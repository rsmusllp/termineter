#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/set_meter_mode.py
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

import struct

from c1218.errors import C1218ReadTableError, C1218WriteTableError
from c1219.constants import C1219_METER_MODE_NAMES, C1219_PROC_RESULT_CODES
from c1219.errors import C1219ProcedureError
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
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
