#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/enum_user_ids.py
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

from time import sleep

from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	connection_state = TermineterModuleOptical.connection_states.none
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Enumerate Valid User IDs From The Device'
		self.detailed_description = 'This module will enumerate existing user IDs from the device.'
		self.options.add_string('USERNAME', 'user name to attempt to log in as', default='0000')
		self.options.add_integer('LOWER', 'user id to start enumerating from', default=0)
		self.options.add_integer('UPPER', 'user id to stop enumerating from', default=50)
		self.advanced_options.add_float('DELAY', 'time in seconds to wait between attempts', default=0.20)

	def run(self):
		conn = self.frmwk.serial_connection
		lower_boundary = self.options['LOWER']
		upper_boundary = self.options['UPPER']
		if lower_boundary > 0xffff:
			self.frmwk.print_error('LOWER option set to high (exceeds 0xffff)')
			return
		if upper_boundary > 0xffff:
			self.frmwk.print_error('UPPER option set to high (exceeds 0xffff)')
			return
		time_delay = self.advanced_options['DELAY']

		self.frmwk.print_status('Enumerating user IDs, please wait...')
		for user_id in range(lower_boundary, (upper_boundary + 1)):
			while not conn.start():
				sleep(time_delay)
			if conn.login(self.options['USERNAME'], user_id):
				self.frmwk.print_good('Found a valid User ID: ' + str(user_id))
			while not conn.stop(force=True):
				sleep(time_delay)
			sleep(time_delay)
		return
