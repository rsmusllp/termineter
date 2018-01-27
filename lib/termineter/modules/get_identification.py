#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/get_identification.py
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

import c1218.data
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	connection_state = TermineterModuleOptical.connection_states.none
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Read And Parse The Identification Information'
		self.detailed_description = 'This module reads and parses the information from the C12.18 identification service.'

	def run(self):
		conn = self.frmwk.serial_connection
		conn.send(c1218.data.C1218IdentRequest())
		resp = c1218.data.C1218Packet(conn.recv())

		self.frmwk.print_status('Received Identity Response:')
		self.frmwk.print_hexdump(resp.data)

		if resp.data[0] != c1218.data.C1218_RESPONSE_CODES['ok']:
			self.frmwk.print_error("Non-ok response status 0x{0} ({1}) received".format(
				resp.data[0],
				c1218.data.C1218_RESPONSE_CODES.get(resp.data[0], 'unknown response code')
			))
		if len(resp.data) < 5:
			self.frmwk.print_error('Received less that the expected amount of data')
			return
		standard, ver, rev = resp.data[1:4]
		standard = {
			0: 'ANSI C12.18',
			1: 'Reserved',
			2: 'ANSI C12.21',
			3: 'ANSI C12.22'
		}.get(standard, "Unknown (0x{0:02x})".format(standard))
		rows = [
			('Reference Standard', standard),
			('Standard Version', "{0}.{1}".format(ver, rev))
		]
		cursor = 4
		if resp.data[cursor] == 0:
			rows.append(('Feature', 'N/A'))
		# the feature list is null terminated as defined in the c12.18 standard
		self.frmwk.print_table(rows, headers=('Name', 'Value'))
