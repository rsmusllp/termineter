#  framework/modules/get_security_info.py
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

from framework.templates import optical_module_template
from c1218.errors import C1218ReadTableError
from c1219.access.security import C1219SecurityAccess
from c1219.constants import C1219_TABLES, C1219_PROCEDURE_NAMES

class Module(optical_module_template):
	def __init__(self, *args, **kwargs):
		optical_module_template.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Get Information About The Meter\'s Access Control'
		self.detailed_description = 'This module reads various tables from 40 to gather information regarding access control. Password constraints, and access permissions to procedures and tables can be gathered with this module.'
	
	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		if not self.frmwk.serial_login():	# don't alert on failed logins
			logger.warning('meter login failed')
		
		try:
			securityCtl = C1219SecurityAccess(conn)
		except C1218ReadTableError:
			self.frmwk.print_error('Could not read necessary tables')
			return
		conn.stop()
		
		security_info = {}
		security_info['Number of Passwords'] = securityCtl.nbr_passwords
		security_info['Max Password Length'] = securityCtl.password_len
		security_info['Number of Keys'] = securityCtl.nbr_keys
		security_info['Number of Permissions'] = securityCtl.nbr_perm_used
		
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
		for idx, entry in securityCtl.passwords.items():
			self.frmwk.print_status(fmt_string.format(idx, entry['password'].encode('hex'), entry['groups']))
		
		self.frmwk.print_status('Table Permissions:')
		fmt_string = "    {0:<64} {1:<14} {2:<14}"
		self.frmwk.print_status(fmt_string.format('Table Number', 'World Readable', 'World Writable'))
		self.frmwk.print_status(fmt_string.format('------------', '--------------', '--------------'))
		fmt_string = "    {0:.<64} {1:<14} {2:<14}"
		for idx, entry in securityCtl.table_permissions.items():
			self.frmwk.print_status(fmt_string.format('#' + str(idx) + ' ' + (C1219_TABLES.get(idx) or 'Unknown'), str(entry['anyread']), str(entry['anywrite'])))
			
		self.frmwk.print_status('Procedure Permissions:')
		fmt_string = "    {0:<64} {1:<14} {2:<16}"
		self.frmwk.print_status(fmt_string.format('Procedure Number', 'World Readable', 'World Executable'))
		self.frmwk.print_status(fmt_string.format('----------------', '--------------', '----------------'))
		fmt_string = "    {0:.<64} {1:<14} {2:<16}"
		for idx, entry in securityCtl.procedure_permissions.items():
			self.frmwk.print_status(fmt_string.format('#' + str(idx) + ' ' + (C1219_PROCEDURE_NAMES.get(idx) or 'Unknown'), str(entry['anyread']), str(entry['anywrite'])))
		
		if len(securityCtl.keys):
			self.frmwk.print_status('Stored Keys:')
			fmt_string = "    {0:<5} {1}"
			self.frmwk.print_status(fmt_string.format('Index', 'Hex Value'))
			self.frmwk.print_status(fmt_string.format('-----', '---------'))
			for idx, entry in securityCtl.keys.items():
				self.frmwk.print_status(fmt_string.format(idx, entry.encode('hex')))
		return
