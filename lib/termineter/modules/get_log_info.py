#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/get_log_info.py
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
from c1219.access.log import C1219LogAccess
from c1219.data import C1219_EVENT_CODES
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
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
