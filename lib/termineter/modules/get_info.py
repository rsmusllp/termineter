#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/get_info.py
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

from c1218.errors import C1218ReadTableError
from c1219.access.general import C1219GeneralAccess
from termineter.module import TermineterModuleOptical

STATUS_FLAGS = flags = (
	'Unprogrammed',
	'Configuration Error',
	'Self Check Error',
	'RAM Failure',
	'ROM Failure',
	'Non Volatile Memory Failure',
	'Clock Error',
	'Measurement Error',
	'Low Battery',
	'Low Loss Potential',
	'Demand Overload',
	'Power Failure',
	'Tamper Detect',
	'Reverse Rotation'
)

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Get Basic Meter Information By Reading Tables'
		self.detailed_description = 'This module retreives some basic meter information and displays it in a human-readable way.'

	def run(self):
		conn = self.frmwk.serial_connection

		try:
			general_ctl = C1219GeneralAccess(conn)
		except C1218ReadTableError:
			self.frmwk.print_error('Could not read the necessary tables')
			return

		meter_info = {}
		meter_info['Character Encoding'] = general_ctl.char_format
		meter_info['Device Type'] = general_ctl.nameplate_type
		meter_info['C12.19 Version'] = {0: 'Pre-release', 1: 'C12.19-1997', 2: 'C12.19-2008'}.get(general_ctl.std_version_no) or 'Unknown'
		meter_info['Manufacturer'] = general_ctl.manufacturer
		meter_info['Model'] = general_ctl.ed_model
		meter_info['Hardware Version'] = str(general_ctl.hw_version_no) + '.' + str(general_ctl.hw_revision_no)
		meter_info['Firmware Version'] = str(general_ctl.fw_version_no) + '.' + str(general_ctl.fw_revision_no)
		meter_info['Serial Number'] = general_ctl.mfg_serial_no

		if general_ctl.ed_mode is not None:
			modes = []
			flags = ['Metering', 'Test Mode', 'Meter Shop Mode', 'Factory']
			for i in range(len(flags)):
				if general_ctl.ed_mode & (2 ** i):
					modes.append(flags[i])
			if len(modes):
				meter_info['Mode Flags'] = ', '.join(modes)

		if general_ctl.std_status is not None:
			status = []
			for i, flag in enumerate(STATUS_FLAGS):
				if general_ctl.std_status & (2 ** i):
					status.append(flag)
			if len(status):
				meter_info['Status Flags'] = ', '.join(status)
		if general_ctl.device_id is not None:
			meter_info['Device ID'] = general_ctl.device_id

		self.frmwk.print_status('General Information:')
		fmt_string = "    {0:.<38}.{1}"
		keys = sorted(list(meter_info.keys()))
		for key in keys:
			self.frmwk.print_status(fmt_string.format(key, meter_info[key]))
