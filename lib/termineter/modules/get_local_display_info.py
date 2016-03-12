#  termineter/modules/get_log_info.py
#
#  Copyright 2016 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
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

from c1219.access.local_display import C1219LocalDisplayAccess
from termineter.templates import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = ['Spencer McIntyre']
		self.description = 'Get Information From The Local Display Tables'
		self.detailed_description = '''\
		Get and display information from the Local Display (3x decade) tables. This information will include what is
		being shown on the meters display and where the data is being read from.
		'''

	def run(self):
		conn = self.frmwk.serial_connection

		loc_disp = C1219LocalDisplayAccess(conn)
		self.frmwk.print_status('Local Display List Records:')
		for entry, record in enumerate(loc_disp.pri_disp_list, 1):
			if entry > 1:
				self.frmwk.print_line('')
			self.frmwk.print_status("  record #{0}".format(entry))
			self.frmwk.print_status("  on time:         {0} seconds ({1}programmable)".format(record.on_time, ('' if loc_disp.on_time_flag else 'non')))
			self.frmwk.print_status("  off time:        {0} seconds ({1}programmable)".format(record.off_time, ('' if loc_disp.off_time_flag else 'non')))
			self.frmwk.print_status("  hold time:       {0} minutes ({1}programmable)".format(record.hold_time, ('' if loc_disp.hold_time_flag else 'non')))
			self.frmwk.print_status("  default list:    {0} ({1})".format(
				record.default_list,
				{
					0: 'comm-link only',
					1: 'normal',
					2: 'alternate',
					3: 'test'
				}.get(record.default_list, 'reserved')
			))
			self.frmwk.print_status("  number of items: {0}".format(record.nbr_items))
		self.frmwk.print_line('')

		self.frmwk.print_status('Local Display List Sources:')
		for source in loc_disp.pri_disp_sources:
			self.frmwk.print_status("  {0:<5}  (0x{0:>04x})".format(source))
