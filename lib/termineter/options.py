#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/options.py
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

import collections.abc
import os

def string_is_hex(string):
	if not len(string):
		return False
	return bool(not filter(lambda c: c not in '0123456789abcdefABCDEF', string))

class Option(object):
	__slots__ = ('callback', 'default', 'help', 'name', 'required', 'type', 'value')
	def __init__(self, name, type, help, required, default=None, callback=None):
		self.name = name
		self.type = type
		self.help = help
		self.required = required
		self.default = default
		self.value = default
		self.callback = callback

	def __repr__(self):
		return "<{0} name='{1}' value={2!r} >".format(self.__class__.__name__, self.name, self.value)

class Options(collections.abc.Mapping):
	"""
	This is a generic options container, it is used to organize framework
	and module options. Once the options are defined and set, the values
	can be retreived by referencing this object like a dictionary such as
	myoptions['OPTIONNAME'] will return 'OPTIONVALUE'
	"""
	def __init__(self, directories):
		"""
		:param directories: An object with attributes of various directories.
		"""
		self.directories = directories
		self._options = {}

	def __getitem__(self, item):
		return self.get_option_value(item)

	def __iter__(self):
		return iter(self._options)

	def __len__(self):
		return len(self._options)

	def add_string(self, name, help, required=True, default=None):
		"""
		Add a new option with a type of String.

		:param str name: The name of the option, how it will be referenced.
		:param str help: The string returned as help to describe how the option is used.
		:param bool required: Whether to require that this option be set or not.
		:param str default: The default value for this option. If required is True and the user must specify it, set to anything but None.
		"""
		self._options[name] = Option(name, 'str', help, required, default=default)

	def add_integer(self, name, help, required=True, default=None):
		"""
		Add a new option with a type of Integer.

		:param str name: The name of the option, how it will be referenced.
		:param str help: The string returned as help to describe how the option is used.
		:param bool required: Whether to require that this option be set or not.
		:param int default: The default value for this option. If required is True and the user must specify it, set to anything but None.
		"""
		self._options[name] = Option(name, 'int', help, required, default=default)

	def add_float(self, name, help, required=True, default=None):
		"""
		Add a new option with a type of Float.

		:param str name: The name of the option, how it will be referenced.
		:param str help: The string returned as help to describe how the option is used.
		:param bool required: Whether to require that this option be set or not.
		:param float default: The default value for this option. If required is True and the user must specify it, set to anything but None.
		"""
		self._options[name] = Option(name, 'flt', help, required, default=default)

	def add_boolean(self, name, help, required=True, default=None):
		"""
		Add a new option with a type of Boolean.

		:param str name: The name of the option, how it will be referenced.
		:param str help: The string returned as help to describe how the option is used.
		:param bool required: Whether to require that this option be set or not.
		:param bool default: The default value for this option. If required is True and the user must specify it, set to anything but None.
		"""
		self._options[name] = Option(name, 'bool', help, required, default=default)

	def add_rfile(self, name, help, required=True, default=None):
		"""
		Add a new option with a type of a readable file. This is the same
		as the string option with the exception that the default value
		will have the following variables replaced within it:
			$USER_DATA The path to the users data directory
			$DATA_PATH The path to the framework's data directory
		This will NOT check that the file exists or is readable.

		:param str name: The name of the option, how it will be referenced.
		:param str help: The string returned as help to describe how the option is used.
		:param bool required: Whether to require that this option be set or not.
		:param str default: The default value for this option. If required is True and the user must specify it, set to anything but None.
		"""
		if isinstance(default, str):
			default = default.replace('$DATA_PATH ', self.directories.data_path + os.path.sep)
			default = default.replace('$USER_DATA ', self.directories.user_data + os.path.sep)
		self._options[name] = Option(name, 'rfile', help, required, default=default)

	def set_callback(self, name, callback):
		"""
		Set a callback function for the specified option. This function is
		called when the option's value changes.

		:param str name: The name of the option to set the callback for.
		:param callback: This function to be called when the option is changed.
		"""
		self.get_option(name).callback = callback

	def set_option_value(self, name, value):
		"""
		Set an option's value.

		:param str name: The name of the option to set the value for.
		:param str value: The value to set the option to, it will be converted from a string.
		:return: The previous value for the specified option.
		"""
		option = self.get_option(name)
		old_value = option.value
		if option.type in ('str', 'rfile'):
			option.value = value
		elif option.type == 'int':
			value = value.lower()
			if not value.isdigit():
				if value.startswith('0x') and string_is_hex(value[2:]):
					value = int(value[2:], 16)
				else:
					raise TypeError('invalid value type')
			option.value = int(value)
		elif option.type == 'flt':
			if value.count('.') > 1:
				raise TypeError('invalid value type')
			if not value.replace('.', '').isdigit():
				raise TypeError('invalid value type')
			option.value = float(value)
		elif option.type == 'bool':
			if value.lower() in ['true', '1', 'on']:
				option.value = True
			elif value.lower() in ['false', '0', 'off']:
				option.value = False
			else:
				raise TypeError('invalid value type')
		else:
			raise Exception('unknown value type')
		if option.callback and not option.callback(value, old_value):
			option.value = old_value
			return False
		return True

	def get_missing_options(self):
		"""
		Get a list of options that are required, but with default values
		of None.
		"""
		return [option.name for option in self._options.values() if option.required and option.value is None]

	def get_option(self, name):
		"""
		Get the option instance.

		:param str name: The name of the option to retrieve.
		:return: The option instance.
		"""
		return self._options[name]

	def get_option_value(self, name):
		return self.get_option(name).value

class AdvancedOptions(Options):
	pass
