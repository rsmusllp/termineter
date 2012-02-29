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
	def __init__(self, directories):
		dict.__init__(self)
		self.directories = directories
	
	def __getitem__(self, name):
		options_def = dict.__getitem__(self, name)
		return options_def[3]
	
	def addString(self, name, help, required = True, default = None):
		self.__setitem__(name, ('str', help, required, default))
	
	def addInteger(self, name, help, required = True, default = None):
		self.__setitem__(name, ('int', help, required, default))
	
	def addFloat(self, name, help, required = True, default = None):
		self.__setitem__(name, ('flt', help, required, default))
	
	def addBoolean(self, name, help, required = True, default = None):
		self.__setitem__(name, ('bool', help, required, default))
	
	def addRFile(self, name, help, required = True, default = None):
		if isinstance(default, str):
			default = default.replace('$USER_DATA ', self.directories.user_data)
			default = default.replace('$MODULES_PATH ', self.directories.modules_path)
			default = default.replace('$DATA_PATH ', self.directories.data_path)
		self.__setitem__(name, ('rfile', help, required, default))
	
	def setOption(self, name, value):
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
		missing_options = []
		for option_name, option_def in self.iteritems():
			if option_def[2] == True and option_def[3] == None:
				missing_options.append(option_name)
		return missing_options
	
	def getOptionValue(self, name):
		if self.__contains__(name) == False:
			raise ValueError('invalid variable\option name')
		options_def = dict.__getitem__(self, name)
		return options_def[3]
	
	def getOptionHelp(self, name):
		if self.__contains__(name) == False:
			raise ValueError('invalid variable\option name')
		options_def = dict.__getitem__(self, name)
		return options_def[1]
