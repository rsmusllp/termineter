#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/get_modem_info.py
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
from c1219.access.telephone import C1219TelephoneAccess
from c1219.data import C1219_CALL_STATUS_FLAGS
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Get Information About The Integrated Modem'
		self.detailed_description = 'This module reads various C12.19 tables from decade 90 to gather information about the integrated modem. If successfully parsed, useful information will be displayed.'

	def run(self):
		conn = self.frmwk.serial_connection

		try:
			telephone_ctl = C1219TelephoneAccess(conn)
		except C1218ReadTableError:
			self.frmwk.print_error('Could not read necessary tables, a modem is not likely present')
			return

		info = {}
		info['Can Answer'] = telephone_ctl.can_answer
		info['Extended Status Available'] = telephone_ctl.use_extended_status
		info['Number of Originating Phone Numbers'] = telephone_ctl.nbr_originate_numbers
		info['PSEM Identity'] = telephone_ctl.psem_identity
		if telephone_ctl.global_bit_rate:
			info['Global Bit Rate'] = telephone_ctl.global_bit_rate
		else:
			info['Originate Bit Rate'] = telephone_ctl.originate_bit_rate
			info['Answer Bit Rate'] = telephone_ctl.answer_bit_rate
		info['Dial Delay'] = telephone_ctl.dial_delay
		if len(telephone_ctl.prefix_number):
			info['Prefix Number'] = telephone_ctl.prefix_number

		keys = info.keys()
		keys.sort()
		self.frmwk.print_status('General Information:')
		fmt_string = "    {0:.<38}.{1}"
		for key in keys:
			self.frmwk.print_status(fmt_string.format(key, info[key]))

		self.frmwk.print_status('Stored Telephone Numbers:')
		fmt_string = "    {0:<6} {1:<16} {2:<32}"
		self.frmwk.print_status(fmt_string.format('Index', 'Number', 'Last Status'))
		self.frmwk.print_status(fmt_string.format('-----', '------', '-----------'))
		for idx, entry in telephone_ctl.originating_numbers.items():
			self.frmwk.print_status(fmt_string.format(entry['idx'], entry['number'].strip(), C1219_CALL_STATUS_FLAGS[entry['status']]))
