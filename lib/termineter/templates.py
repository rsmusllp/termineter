#  termineter/templates.py
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

from termineter.options import AdvancedOptions, Options

class TermineterModule(object):
	frmwk_required_options = ()

	def __init__(self, frmwk):
		self.frmwk = frmwk

		self.name = 'unknown'
		self.version = 0
		self.author = ['anonymous']
		self.description = 'This module is undocumented.'
		self.detailed_description = 'This module is undocumented.'
		self.options = Options(frmwk.directories)
		self.advanced_options = AdvancedOptions(frmwk.directories)

	def __repr__(self):
		return '<' + self.__class__.__name__ + ' ' + self.name + ' >'

	def get_missing_options(self):
		frmwk_missing_options = self.frmwk.options.get_missing_options()
		frmwk_missing_options.extend(self.frmwk.advanced_options.get_missing_options())

		missing_options = []
		for required_option in self.frmwk_required_options:
			if required_option in frmwk_missing_options:
				missing_options.append(required_option)
		missing_options.extend(self.options.get_missing_options())
		missing_options.extend(self.advanced_options.get_missing_options())
		return missing_options

	@property
	def logger(self):
		return self.frmwk.get_module_logger(self.name)

class TermineterModuleOptical(TermineterModule):
	frmwk_required_options = (
		'CONNECTION',
		'USERNAME',
		'USERID',
		'PASSWORD',
		'PASSWORDHEX',
		'BAUDRATE',
		'BYTESIZE',
		'CACHETBLS',
		'STOPBITS',
		'NBRPKTS',
		'PKTSIZE'
	)
	require_connection = True
	attempt_login = True
	def __init__(self, *args, **kwargs):
		super(TermineterModuleOptical, self).__init__(*args, **kwargs)

class TermineterModuleRfcat(TermineterModule):
	pass
