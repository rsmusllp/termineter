#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/get_local_display_info.py
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

from c1219.access.local_display import C1219LocalDisplayAccess
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
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
