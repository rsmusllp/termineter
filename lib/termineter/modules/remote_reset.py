#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/remote_reset.py
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

import struct

from c1218.errors import C1218ReadTableError, C1218WriteTableError
from c1219.errors import C1219ProcedureError
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Initiate A Reset Procedure'
		self.detailed_description = 'Initiate a remote reset procedure. Despite the name, this module is used locally through the optical interface.'
		self.options.add_boolean('DEMAND', 'perform a demand reset', default=False)
		self.options.add_boolean('SELF_READ', 'perform a self read', default=False)

	def run(self):
		conn = self.frmwk.serial_connection

		params = 0
		if self.options['DEMAND']:
			params |= 0b01
		if self.options['SELF_READ']:
			params |= 0b10

		self.frmwk.print_status('Initiating Reset Procedure')

		try:
			conn.run_procedure(9, False, struct.pack('B', params))
		except (C1218ReadTableError, C1218WriteTableError, C1219ProcedureError) as error:
			self.frmwk.print_exception(error)
		else:
			self.frmwk.print_good('Successfully Reset The Meter')
