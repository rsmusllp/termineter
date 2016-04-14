#  termineter/options.py
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

import os

def string_is_hex(string):
	if not len(string):
		return False
	return bool(not filter(lambda c: c not in '0123456789abcdefABCDEF', string))

class Options(dict):
	"""
	This is a generic options container, it is used to organize framework
	and module options. Once the options are defined and set, the values
	can be retreived by referencing this object like a dictionary such as
	myoptions['OPTIONNAME'] will return 'OPTIONVALUE'
	"""
	def __init__(self, directories):
		"""
		Initializes a new Options instance

		@type directories: Namespace
		@param directories: An object with attributes of various
		directories.
		"""
		dict.__init__(self)
		self.directories = directories

	def __getitem__(self, name):
		options_def = dict.__getitem__(self, name)
		return options_def[3]

	def add_string(self, name, help, required=True, default=None):
		"""
		Add a new option with a type of String.

		@type name: String
		@param name: The name of the option, how it will be referenced.

		@type help: String
		@param help: The string returned as help to describe how the option
		is used.

		@type required: Boolean
		@param required: Whether to require that this option be set or not.

		@type default: String
		@param default: The default value for this option. If required is
		True and the user must specify it, set to anything but None.
		"""
		self.__setitem__(name, ('str', help, required, default, None))

	def add_integer(self, name, help, required=True, default=None):
		"""
		Add a new option with a type of Integer.

		@type name: String
		@param name: The name of the option, how it will be referenced.

		@type help: String
		@param help: The string returned as help to describe how the option
		is used.

		@type required: Boolean
		@param required: Whether to require that this option be set or not.

		@type default: Integer
		@param default: The default value for this option. If required is
		True and the user must specify it, set to anything but None.
		"""
		self.__setitem__(name, ('int', help, required, default, None))

	def add_float(self, name, help, required=True, default=None):
		"""
		Add a new option with a type of Float.

		@type name: String
		@param name: The name of the option, how it will be referenced.

		@type help: String
		@param help: The string returned as help to describe how the option
		is used.

		@type required: Boolean
		@param required: Whether to require that this option be set or not.

		@type default: Float
		@param default: The default value for this option. If required is
		True and the user must specify it, set to anything but None.
		"""
		self.__setitem__(name, ('flt', help, required, default, None))

	def add_boolean(self, name, help, required=True, default=None):
		"""
		Add a new option with a type of Boolean.

		@type name: String
		@param name: The name of the option, how it will be referenced.

		@type help: String
		@param help: The string returned as help to describe how the option
		is used.

		@type required: Boolean
		@param required: Whether to require that this option be set or not.

		@type default: Boolean
		@param default: The default value for this option. If required is
		True and the user must specify it, set to anything but None.
		"""
		self.__setitem__(name, ('bool', help, required, default, None))

	def add_rfile(self, name, help, required=True, default=None):
		"""
		Add a new option with a type of a readable file. This is the same
		as the string option with the exception that the default value
		will have the following variables replaced within it:
			$USER_DATA The path to the users data directory
			$MODULES_PATH The path to where modules are stored
			$DATA_PATH The path to the framework's data directory
		This will NOT check that the file exists or is readable.

		@type name: String
		@param name: The name of the option, how it will be referenced.

		@type help: String
		@param help: The string returned as help to describe how the option
		is used.

		@type required: Boolean
		@param required: Whether to require that this option be set or not.

		@type default: String
		@param default: The default value for this option. If required is
		True and the user must specify it, set to anything but None.
		"""
		if isinstance(default, str):
			default = default.replace('$USER_DATA ', self.directories.user_data + os.path.sep)
			default = default.replace('$MODULES_PATH ', self.directories.modules_path + os.path.sep)
			default = default.replace('$DATA_PATH ', self.directories.data_path + os.path.sep)
		self.__setitem__(name, ('rfile', help, required, default, None))

	def set_callback(self, name, callback):
		"""
		Set an options value

		@type name: String
		@param name: The options name that is to be changed

		@type callback: Function
		@param callback: This function will be called when the set_option()
		is called and will be passed a single parameter of the value that
		is being set.  It will be called prior to the value being set and
		an exception can be thrown to alert the user that the value is invalid.
		"""
		if not self.__contains__(name):
			raise ValueError('invalid variable\option name')
		options_def = dict.__getitem__(self, name)
		self.__setitem__(name, (options_def[0], options_def[1], options_def[2], options_def[3], callback))

	def set_option(self, name, value):
		"""
		Set an options value

		@type name: String
		@param name: The options name that is to be changed

		@type value: *
		@param value: The value to set the option to, the type must be the
		same as it was defined with using the addX function.
		"""
		if not self.__contains__(name):
			raise ValueError('invalid variable\\option name')
		options_def = dict.__getitem__(self, name)
		if options_def[0] in ['str', 'rfile']:
			pass
		elif options_def[0] == 'int':
			value = value.lower()
			if not value.isdigit():
				if value.startswith('0x') and string_is_hex(value[2:]):
					value = int(value[2:], 16)
				else:
					raise TypeError('invalid value type')
			value = int(value)
		elif options_def[0] == 'flt':
			if value.count('.') > 1:
				raise TypeError('invalid value type')
			if not value.replace('.', '').isdigit():
				raise TypeError('invalid value type')
			value = float(value)
		elif options_def[0] == 'bool':
			if value.lower() in ['true', '1', 'on']:
				value = True
			elif value.lower() in ['false', '0', 'off']:
				value = False
			else:
				raise TypeError('invalid value type')
		else:
			raise Exception('unknown value type')
		if options_def[4]:
			options_def[4](value)
		self.__setitem__(name, (options_def[0], options_def[1], options_def[2], value, options_def[4]))

	def get_missing_options(self):
		"""
		Get a list of options that are required, but with default values
		of None.
		"""
		missing_options = []
		for option_name, option_def in self.items():
			if option_def[2] and option_def[3] is None:
				missing_options.append(option_name)
		return missing_options

	def get_option_value(self, name):
		"""
		Return an options value.

		@type name: String
		@param name: The name of the option who's value is to be returned.
		"""
		if not self.__contains__(name):
			raise ValueError('invalid variable\option name')
		options_def = dict.__getitem__(self, name)
		return options_def[3]

	def get_option_help(self, name):
		"""
		Return an options help string.

		@type name: String
		@param name: The name of the option who's help string is to be
		returned.
		"""
		if not self.__contains__(name):
			raise ValueError('invalid variable\option name')
		options_def = dict.__getitem__(self, name)
		return options_def[1]

class AdvancedOptions(Options):
	pass
