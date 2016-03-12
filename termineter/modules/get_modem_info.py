#  termineter/modules/get_modem_info.py
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

from c1218.errors import C1218ReadTableError
from c1219.access.telephone import C1219TelephoneAccess
from c1219.data import C1219_CALL_STATUS_FLAGS
from termineter.templates import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = ['Spencer McIntyre']
		self.description = 'Get Information About The Integrated Modem'
		self.detailed_description = 'This module reads various C1219 tables from decade 90 to gather information about the integrated modem. If successfully parsed, useful information will be displayed.'

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
