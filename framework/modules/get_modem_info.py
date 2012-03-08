#  framework/modules/get_modem_info.py
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

from framework.templates import module_template
from c1218.errors import C1218ReadTableError
from c1219.data import C1219_CALL_STATUS_FLAGS
from c1219.access.telephone import C1219TelephoneAccess
from struct import pack, unpack

class Module(module_template):
	def __init__(self, *args, **kwargs):
		module_template.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Get Information About The Integrated Modem'
		self.detailed_description = 'This module reads various C1219 tables from decade 90 to gather information about the integrated modem. If successfully parsed, useful information will be displayed.'
	
	def run(self, frmwk, args):
		logger = frmwk.get_module_logger(self.name)
		if not frmwk.serial_login():	# don't alert on failed logins
			logger.warning('meter login failed')
		conn = frmwk.serial_connection
		
		try:
			telephoneCtl = C1219TelephoneAccess(conn)
		except C1218ReadTableError:
			frmwk.print_error('Could not read necessary tables, a modem is not likely present')
			return
		conn.stop()
		
		info = {}
		info['Can Answer'] = telephoneCtl.can_answer
		info['Extended Status Available'] = telephoneCtl.use_extended_status
		info['Number of Originating Phone Numbers'] = telephoneCtl.nbr_originate_numbers
		info['PSEM Identity'] = telephoneCtl.psem_identity
		if telephoneCtl.global_bit_rate:
			info['Global Bit Rate'] = telephoneCtl.global_bit_rate
		else:
			info['Originate Bit Rate'] = telephoneCtl.originate_bit_rate
			info['Answer Bit Rate'] = telephoneCtl.answer_bit_rate
		info['Dial Delay'] = telephoneCtl.dial_delay
		if len(telephoneCtl.prefix_number):
			info['Prefix Number'] = telephoneCtl.prefix_number
		
		keys = info.keys()
		keys.sort()
		frmwk.print_status('General Information:')
		fmt_string = "    {0:.<38}.{1}"
		for key in keys:
			frmwk.print_status(fmt_string.format(key, info[key]))
		
		frmwk.print_status('Stored Telephone Numbers:')
		fmt_string = "    {0:<6} {1:<16} {2:<32}"
		frmwk.print_status(fmt_string.format('Index', 'Number', 'Last Status'))
		frmwk.print_status(fmt_string.format('-----', '------', '-----------'))
		for idx, entry in telephoneCtl.originating_numbers.items():
			frmwk.print_status(fmt_string.format(entry['idx'], entry['number'].strip(), C1219_CALL_STATUS_FLAGS[entry['status']]))
