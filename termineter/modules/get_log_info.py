#  termineter/modules/get_log_info.py
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
from c1219.access.log import C1219LogAccess
from c1219.data import C1219_EVENT_CODES
from termineter.templates import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = ['Spencer McIntyre']
		self.description = 'Get Information About The Meter\'s Logs'
		self.detailed_description = """\
		This module reads various C1219 tables from decade 70 to gather log information from the smart meter. If
		successful the parsed contents of the logs will be displayed.
		"""

	def run(self):
		conn = self.frmwk.serial_connection

		try:
			log_ctl = C1219LogAccess(conn)
		except C1218ReadTableError:
			self.frmwk.print_error('Could not read necessary tables, logging may not be enabled')
			return

		if len(log_ctl.logs) == 0:
			self.frmwk.print_status('Log History Table Contains No Entries')
			return
		else:
			self.frmwk.print_status('Log History Table Contains ' + str(log_ctl.nbr_history_entries) + ' Entries')
		log_entry = log_ctl.logs[0]
		topline = ''
		line = ''
		if 'Time' in log_entry:
			topline += "{0:<19} ".format('Time Stamp')
			line += "{0:<19} ".format('----------')
		if 'Event Number' in log_entry:
			topline += "{0:<5} ".format('Event Number')
			line += "{0:<5} ".format('------------')
		topline += "{0:<6} {1:<58} {2}".format('UID', 'Procedure Number', 'Arguments')
		line += "{0:<6} {1:<58} {2}".format('---', '----------------', '---------')
		self.frmwk.print_line(topline)
		self.frmwk.print_line(line)
		for log_entry in log_ctl.logs:
			line = ''
			if 'Time' in log_entry:
				topline += "{0:<19} ".format('Time Stamp')
				line += "{0:<19} ".format(log_entry['Time'])
			if 'Event Number' in log_entry:
				topline += "{0:<5} ".format('Event Number')
				line += "{0:<5} ".format(log_entry['Event Number'])
			line += "{0:<6} {1:<58} {2}".format(log_entry['User ID'], C1219_EVENT_CODES[log_entry['Procedure Number']], log_entry['Arguments'].encode('hex'))
			self.frmwk.print_line(line)

