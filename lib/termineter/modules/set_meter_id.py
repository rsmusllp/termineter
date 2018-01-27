#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/set_meter_id.py
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

from c1219.access.general import C1219GeneralAccess
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Set The Meter\'s I.D.'
		self.detailed_description = 'This module will over write the Smart Meter\'s device ID with the new value specified in METER_ID.'
		self.options.add_string('METER_ID', 'value to set the meter id to', True)

	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		meter_id = self.options['METER_ID']

		gen_ctl = C1219GeneralAccess(conn)
		if gen_ctl.id_form == 0:
			logger.info('device id stored in 20 byte string')
			if len(meter_id) > 20:
				self.frmwk.print_error('METER_ID length exceeds the allowed 20 bytes')
				return
		else:
			logger.info('device id stored in BCD(10)')
			if len(meter_id) > 10:
				self.frmwk.print_error('METER_ID length exceeds the allowed 10 bytes')
				return
		if gen_ctl.set_device_id(meter_id):
			self.frmwk.print_error('Could not set the Meter\'s ID')
		else:
			self.frmwk.print_status('Successfully updated the Meter\'s ID to: ' + meter_id)
