#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/get_security_info.py
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
from c1219.access.security import C1219SecurityAccess
from c1219.constants import C1219_TABLES, C1219_PROCEDURE_NAMES
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Get Information About The Meter\'s Access Control'
		self.detailed_description = 'This module reads various tables from 40 to gather information regarding access control. Password constraints, and access permissions to procedures and tables can be gathered with this module.'

	def run(self):
		conn = self.frmwk.serial_connection

		try:
			security_ctl = C1219SecurityAccess(conn)
		except C1218ReadTableError:
			self.frmwk.print_error('Could not read necessary tables')
			return

		security_info = {}
		security_info['Number of Passwords'] = security_ctl.nbr_passwords
		security_info['Max Password Length'] = security_ctl.password_len
		security_info['Number of Keys'] = security_ctl.nbr_keys
		security_info['Number of Permissions'] = security_ctl.nbr_perm_used

		self.frmwk.print_status('Security Information:')
		fmt_string = "    {0:.<38}.{1}"
		keys = security_info.keys()
		keys.sort()
		for key in keys:
			self.frmwk.print_status(fmt_string.format(key, security_info[key]))

		self.frmwk.print_status('Passwords and Permissions:')
		fmt_string = "    {0:<5} {1:<40} {2}"
		self.frmwk.print_status(fmt_string.format('Index', 'Password (In Hex)', 'Group Flags'))
		self.frmwk.print_status(fmt_string.format('-----', '-----------------', '-----------'))
		for idx, entry in security_ctl.passwords.items():
			self.frmwk.print_status(fmt_string.format(idx, entry['password'].encode('hex'), entry['groups']))

		self.frmwk.print_status('Table Permissions:')
		fmt_string = "    {0:<64} {1:<14} {2:<14}"
		self.frmwk.print_status(fmt_string.format('Table Number', 'World Readable', 'World Writable'))
		self.frmwk.print_status(fmt_string.format('------------', '--------------', '--------------'))
		fmt_string = "    {0:.<64} {1:<14} {2:<14}"
		for idx, entry in security_ctl.table_permissions.items():
			self.frmwk.print_status(fmt_string.format('#' + str(idx) + ' ' + (C1219_TABLES.get(idx) or 'Unknown'), str(entry['anyread']), str(entry['anywrite'])))

		self.frmwk.print_status('Procedure Permissions:')
		fmt_string = "    {0:<64} {1:<14} {2:<16}"
		self.frmwk.print_status(fmt_string.format('Procedure Number', 'World Readable', 'World Executable'))
		self.frmwk.print_status(fmt_string.format('----------------', '--------------', '----------------'))
		fmt_string = "    {0:.<64} {1:<14} {2:<16}"
		for idx, entry in security_ctl.procedure_permissions.items():
			self.frmwk.print_status(fmt_string.format('#' + str(idx) + ' ' + (C1219_PROCEDURE_NAMES.get(idx) or 'Unknown'), str(entry['anyread']), str(entry['anywrite'])))

		if len(security_ctl.keys):
			self.frmwk.print_status('Stored Keys:')
			fmt_string = "    {0:<5} {1}"
			self.frmwk.print_status(fmt_string.format('Index', 'Hex Value'))
			self.frmwk.print_status(fmt_string.format('-----', '---------'))
			for idx, entry in security_ctl.keys.items():
				self.frmwk.print_status(fmt_string.format(idx, entry.encode('hex')))
		return
