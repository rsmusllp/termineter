#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/module.py
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

import collections
import collections.abc
import enum
import importlib
import logging

import termineter.errors
import termineter.options

import pluginbase

_ModuleReference = collections.namedtuple('_ModuleReference', ('instance', 'pymodule'))

class ConnectionState(enum.Enum):
	none = 'none'
	connected = 'connected'
	authenticated = 'authenticated'

class ManagerManager(collections.abc.Mapping):
	def __init__(self, frmwk, searchpath):
		self.logger = logging.getLogger('termineter.module_manager')
		self.frmwk = frmwk
		self.source = pluginbase.PluginBase(package='termineter.modules').make_plugin_source(
			searchpath=searchpath
		)
		self._modules = {}
		for module_id in self.source.list_plugins():
			self._init_pymodule(self.source.load_plugin(module_id))

	def __getitem__(self, item):
		return self._modules[item].instance

	def __iter__(self):
		return iter(self._modules)

	def __len__(self):
		return len(self._modules)

	def _init_pymodule(self, pymodule):
		module_id = pymodule.__name__.split('.', 3)[-1]
		if not hasattr(pymodule, 'Module'):
			self.logger.error('module: ' + module_id + ' is missing the Module class')
			return
		if not issubclass(pymodule.Module, TermineterModule):
			self.logger.error('module: ' + module_id + ' is not derived from the TermineterModule class')
			return

		module_instance = pymodule.Module(self.frmwk)
		if not isinstance(module_instance.options, termineter.options.Options):
			self.logger.critical('module: ' + module_id + ' options must be an Options instance')
			raise termineter.errors.FrameworkRuntimeError('options must be a termineter.options.Options instance')
		if not isinstance(module_instance.advanced_options, termineter.options.Options):
			self.logger.critical('module: ' + module_id + ' advanced_options must be an Options instance')
			raise termineter.errors.FrameworkRuntimeError('advanced_options must be a termineter.options.Options instance')

		self._modules[module_instance.name] = _ModuleReference(instance=module_instance, pymodule=pymodule)
		return module_instance

	def reload(self, module_path):
		modref = self._modules[module_path]
		importlib.reload(modref.pymodule)
		return self._init_pymodule(modref.pymodule)

class TermineterModule(object):
	frmwk_required_options = ()
	def __init__(self, frmwk):
		self.frmwk = frmwk
		self.author = ['Anonymous']
		self.description = 'This module is undocumented.'
		self.detailed_description = 'This module is undocumented.'
		self.options = termineter.options.Options(frmwk.directories)
		self.advanced_options = termineter.options.AdvancedOptions(frmwk.directories)

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

	@property
	def name(self):
		return self.path.split('/')[-1]

	@property
	def path(self):
		return self.__module__.split('.', 3)[-1].replace('.', '/')

	def run(self):
		raise NotImplementedError()

class TermineterModuleOptical(TermineterModule):
	frmwk_required_options = (
		'SERIAL_CONNECTION',
		'USERNAME',
		'USER_ID',
		'PASSWORD',
		'PASSWORD_HEX',
		'SERIAL_BAUD_RATE',
		'SERIAL_BYTE_SIZE',
		'CACHE_TABLES',
		'SERIAL_STOP_BITS',
		'NUMBER_PACKETS',
		'PACKET_SIZE'
	)
	connection_state = ConnectionState.authenticated
	connection_states = ConnectionState
	def __init__(self, *args, **kwargs):
		super(TermineterModuleOptical, self).__init__(*args, **kwargs)

	@property
	def connection(self):
		return self.frmwk.serial_connection
