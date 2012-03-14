#  framework/options.py
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
	
	def addString(self, name, help, required = True, default = None):
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
		self.__setitem__(name, ('str', help, required, default))
	
	def addInteger(self, name, help, required = True, default = None):
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
		self.__setitem__(name, ('int', help, required, default))
	
	def addFloat(self, name, help, required = True, default = None):
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
		self.__setitem__(name, ('flt', help, required, default))
	
	def addBoolean(self, name, help, required = True, default = None):
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
		self.__setitem__(name, ('bool', help, required, default))
	
	def addRFile(self, name, help, required = True, default = None):
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
			default = default.replace('$USER_DATA ', self.directories.user_data)
			default = default.replace('$MODULES_PATH ', self.directories.modules_path)
			default = default.replace('$DATA_PATH ', self.directories.data_path)
		self.__setitem__(name, ('rfile', help, required, default))
	
	def setOption(self, name, value):
		"""
		Set an options value
		
		@type name: String
		@param name: The options name that is to be changed
		
		@type value: *
		@param value: The value to set the option to, the type must be the
		same as it was defined with using the addX function.
		"""
		if self.__contains__(name) == False:
			raise ValueError('invalid variable\option name')
		options_def = dict.__getitem__(self, name)
		if options_def[0] in [ 'str', 'rfile' ]:
			pass
		elif options_def[0] == 'int':
			if not value.isdigit():
				raise TypeError('invalid value type')
			value = int(value)
		elif options_def[0] == 'flt':
			if not value.replace('.').isdigit():
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
			raise Exception('Unknown value type')
		self.__setitem__(name, (options_def[0], options_def[1], options_def[2], value))
	
	def getMissingOptions(self):
		"""
		Get a list of options that are required, but with default values
		of None.
		"""
		missing_options = []
		for option_name, option_def in self.iteritems():
			if option_def[2] == True and option_def[3] == None:
				missing_options.append(option_name)
		return missing_options
	
	def getOptionValue(self, name):
		"""
		Return an options value.
		
		@type name: String
		@param name: The name of the option who's value is to be returned.
		"""
		if self.__contains__(name) == False:
			raise ValueError('invalid variable\option name')
		options_def = dict.__getitem__(self, name)
		return options_def[3]
	
	def getOptionHelp(self, name):
		"""
		Return an options help string.
		
		@type name: String
		@param name: The name of the option who's help string is to be
		returned.
		"""
		if self.__contains__(name) == False:
			raise ValueError('invalid variable\option name')
		options_def = dict.__getitem__(self, name)
		return options_def[1]
