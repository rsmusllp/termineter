#  framework/core.py
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

import os
import re
import sys
import serial
import logging
import logging.handlers
from binascii import unhexlify
from serial.serialutil import SerialException
from framework.options import Options
from framework.templates import module_template
from c1218.connection import Connection
from c1218.errors import C1218IOError, C1218ReadTableError

DEFAULT_SERIAL_SETTINGS = {'parity': serial.PARITY_NONE, 'baudrate': 9600, 'bytesize': serial.EIGHTBITS, 'xonxoff': False, 'interCharTimeout': None, 'rtscts': False, 'timeout': 1, 'stopbits': serial.STOPBITS_ONE, 'dsrdtr': False, 'writeTimeout': None}

class FrameworkConfigurationError(Exception):
	def __init__(self, msg):
		self.msg = msg
	
	def __str__(self):
		return repr(self.msg)

class Namespace:
	"""
	This class is used to hold attributes of the framework.  It doesn't
	really do anything, it's used for organizational purposes only.
	"""
	pass
	
class Framework(object):
	"""
	This is the main instance of the framework.  It contains and 
	manages the serial connection as well as all of the loaded 
	modules.
	"""
	def __init__(self):
		self.modules = { }
		self.__serial_connected__ = False
		self.__package__ = '.'.join(self.__module__.split('.')[:-1])
		package_path = __import__(self.__package__, None, None, ['__path__']).__path__[0]	# that's some python black magic trickery for you
		
		self.directories = Namespace()
		self.directories.user_data = os.path.expanduser('~') + os.sep + '.termineter' + os.sep
		self.directories.modules_path = package_path + os.sep + 'modules' + os.sep
		self.directories.data_path = package_path + os.sep + 'data' + os.sep
		if not os.path.isdir(self.directories.user_data):
			os.mkdir(self.directories.user_data)
		self.serial_connection = None
		self.logger = logging.getLogger(self.__package__ + '.core')
		main_file_handler = logging.handlers.RotatingFileHandler(self.directories.user_data + self.__package__ + '.log', maxBytes = 262144, backupCount = 5)
		main_file_handler.setLevel(logging.DEBUG)
		main_file_handler.setFormatter(logging.Formatter("%(asctime)s %(name)-50s %(levelname)-10s %(message)s"))
		logging.getLogger('').addHandler(main_file_handler)
		self.options = Options(self.directories)
		self.options.addBoolean('USECOLOR', 'enable color on the console interface', default = False)
		self.options.addString('CONNECTION', 'serial connection string', True)
		self.options.addString('USERNAME', 'serial username', default = '0000')
		self.options.addInteger('USERID', 'serial userid', default = 0)
		self.options.addString('PASSWORD', 'serial c12.18 password', default = '00000000000000000000')
		self.options.addBoolean('PASSWORDHEX', 'if the password is in hex', default = True)
		self.advanced_options = Options(self.directories)
		self.advanced_options.addInteger('BAUDRATE', 'serial connection baud rate', default = 9600)
		self.advanced_options.addInteger('BYTESIZE', 'serial connection byte size', default = serial.EIGHTBITS)
		self.advanced_options.addInteger('STOPBITS', 'serial connection stop bits', default = serial.STOPBITS_ONE)
		if sys.platform.startswith('linux'):
			self.options.setOption('USECOLOR', 'True')
		if not os.path.isdir(self.directories.data_path):
			self.logger.critical('path to data not found')
			raise FrameworkConfigurationError('path to data not found')
		modules_path = self.directories.modules_path
		self.logger.debug('searching for modules in: ' + modules_path)
		self.current_module = None
		if not os.path.isdir(modules_path):
			self.logger.critical('path to modules not found')
			raise FrameworkConfigurationError('path to modules not found')
		all_modules = os.listdir(modules_path)
		loadable_modules = os.listdir(modules_path)
		for module in all_modules:										# get rid of ones we don't want to load
			if not module.endswith('.py'):
				loadable_modules.remove(module)
				continue
			if module.startswith('__'):
				loadable_modules.remove(module)
				continue
			if module.lower() != module:
				loadable_modules.remove(module)							# only lower case names please
		del all_modules
		
		for module_name in loadable_modules:
			module_name = module_name[:-3]
			self.logger.debug('loading module: ' + module_name)
			module = __import__(self.__package__ + '.modules.' + module_name, None, None, ['Module'])
			module_instance = module.Module(self.directories)
			if not isinstance(module_instance, module_template):
				self.logger.error('module: ' + module_name + ' is not derived from the module_template class')
				continue
			if not hasattr(module_instance, 'run'):
				self.logger.critical('module: ' + module_name + ' has no run() function')
				raise Exception('module: ' + module_name + ' has no run() function')
			if not isinstance(module_instance.options, Options) or not isinstance(module_instance.advanced_options, Options):
				self.logger.critical('module: ' + module_name + ' options and advanced_options must be Options instances')
				raise Exception('options and advanced_options must be Options instances')
			module_instance.name = module_name
			self.modules[module_name] = module_instance
		self.logger.info('successfully loaded ' + str(len(self.modules)) + ' modules into the framework')
	
	def __repr__(self):
		return '<' + self.__class__.__name__ + ' Loaded Modules: ' + str(len(self.modules)) + ', Serial Connected: ' + str(self.is_serial_connected()) + ' >'
	
	def reload_module(self, module_name = None):
		"""
		Reloads a module into the framework.  If module_name is not
		specified, then the curent_module variable is used.  Returns True
		on success, False on error.
		
		@type module_name: String
		@param module_name: The name of the module to reload
		"""
		if module_name == None:
			if self.current_module != None:
				module_name = self.current_module
			else:
				self.logger.warning('must specify module if not module is currently being used')
				return False
		if not module_name + '.py' in os.listdir(self.directories.modules_path):
			self.logger.error('invalid module name requested for reload')
			return False
		self.logger.info('reloading module: ' + module_name)
		module = __import__(self.__package__ + '.modules.' + module_name, None, None, ['Module'])
		reload(module)
		module_instance = module.Module(self.directories)
		if not isinstance(module_instance, module_template):
			self.logger.error('module: ' + module_name + ' is not derived from the module_template class')
			raise Exception('module: ' + module_name + ' is not derived from the module_template class')
		if not hasattr(module_instance, 'run'):
			self.logger.error('module: ' + module_name + ' has no run() function')
			raise Exception('module: ' + module_name + ' has no run() function')
		if not isinstance(module_instance.options, Options) or not isinstance(module_instance.advanced_options, Options):
			self.logger.error('module: ' + module_name + ' options and advanced_options must be Options instances')
			raise Exception('options and advanced_options must be Options instances')
		module_instance.name = module_name
		self.modules[module_name] = module_instance
		return True
	
	@property
	def use_colors(self):
		return self.options['USECOLOR']
	
	@use_colors.setter
	def use_colors(self, value):
		self.options.setOption('USECOLOR', str(value))
	
	def get_module_logger(self, name):
		"""
		This returns a logger for individual modules to allow them to be
		inherited from the framework and thus be named appropriately.
		
		@type name: String
		@param name: The name of the module requesting the logger
		"""
		return logging.getLogger(self.__package__ + '.modules.' + name)

	def print_error(self, message):
		if self.options['USECOLOR']:
			print '\033[1;31m[-] \033[1;m' + (os.linesep + '\033[1;31m[-] \033[1;m').join(message.split(os.linesep))
		else:
			print '[-] ' + (os.linesep + '[-] ').join(message.split(os.linesep))

	def print_good(self, message):
		if self.options['USECOLOR']:
			print '\033[1;32m[+] \033[1;m' + (os.linesep + '\033[1;32m[+] \033[1;m').join(message.split(os.linesep))
		else:
			print '[+] ' + (os.linesep + '[+] ').join(message.split(os.linesep))

	def print_line(self, message):
		print message

	def print_status(self, message):
		if self.options['USECOLOR']:
			print '\033[1;34m[*] \033[1;m' + (os.linesep + '\033[1;34m[*] \033[1;m').join(message.split(os.linesep))
		else:
			print '[*] ' + (os.linesep + '[*] ').join(message.split(os.linesep))

	def print_hexdump(self, data):
		x = str(data)
		l = len(x)
		i = 0
		while i < l:
			print "%04x  " % i,
			for j in range(16):
				if i+j < l:
					print "%02X" % ord(x[i+j]),
				else:
					print "  ",
				if j%16 == 7:
					print "",
			print " ",
			r = ""
			for j in x[i:i+16]:
				j = ord(j)
				if (j < 32) or (j >= 127):
					r = r + "."
				else:
					r = r + chr(j)
			print r
			i += 16

	def is_serial_connected(self):
		"""
		Returns True if the serial interface is connected.
		"""
		return self.__serial_connected__
	
	def serial_disconnect(self):
		"""
		Closes the serial connection to the meter and disconnects from the
		device.
		"""
		if self.__serial_connected__:
			try:
				self.serial_connection.close()
			except C1218IOError as error:
				self.logger.error('caught C1218IOError: ' + str(error))
			except SerialException as error:
				self.logger.error('caught SerialException: ' + str(error))
			self.__serial_connected__ = False
			self.logger.warning('the serial interface has been disconnected')
		return True

	def serial_connect(self):
		"""
		Connect to the serial device and then verifies that the meter is
		responding.  Once the serial device is opened, this function attempts
		to retreive the contents of table #0 (GEN_CONFIG_TBL) to configure
		the endianess it will use.  Returns True on success.
		"""
		username = self.options['USERNAME']
		userid = self.options['USERID']
		if len(username) > 10:
			self.logger.error('username cannot be longer than 10 characters')
			raise FrameworkConfigurationError('username cannot be longer than 10 characters')
		if not (0 <= userid <= 0xffff):
			self.logger.error('user id must be between 0 and 0xffff')
			raise FrameworkConfigurationError('user id must be between 0 and 0xffff')
		frmwk_serial_settings = {'parity':serial.PARITY_NONE,
			'baudrate': self.advanced_options['BAUDRATE'],
			'bytesize': self.advanced_options['BYTESIZE'],
			'xonxoff': False,
			'interCharTimeout': None,
			'rtscts': False,
			'timeout': 1,
			'stopbits': self.advanced_options['STOPBITS'],
			'dsrdtr': False,
			'writeTimeout': None}
		self.logger.info('opening serial device: ' + self.options['CONNECTION'])
		
		try:
			self.serial_connection = Connection(self.options['CONNECTION'], frmwk_serial_settings, enable_cache = True)
		except Exception as error:
			self.logger.error('could not open the serial device')
			raise error
		
		try:
			self.serial_connection.start()
			if not self.serial_connection.login(username, userid):
				self.logger.error('the meter has rejected the username and userid')
				raise FrameworkConfigurationError('the meter has rejected the username and userid')
		except C1218IOError as error:
			self.logger.error('serial connection has been opened but the meter is unresponsive')
			raise error
		
		try:
			general_config_table = self.serial_connection.getTableData(0)
		except C1218ReadTableError as error:
			self.logger.error('serial connection as been opened but the general configuration table (table #0) could not be read')
			raise error
		
		if (ord(general_config_table[0]) & 1):
			self.logger.info('setting the connection to use big-endian for C1219 data')
			self.serial_connection.c1219_endian = '>'
		else:
			self.logger.info('setting the connection to use little-endian for C1219 data')
			self.serial_connection.c1219_endian = '<'
		
		try:
			self.serial_connection.stop()
		except C1218IOError as error:
			self.logger.error('serial connection has been opened but the meter is unresponsive')
			raise error
		
		self.__serial_connected__ = True
		self.logger.warning('the serial interface has been connected')
		return True
	
	def serial_login(self):
		"""
		Attempt to log into the meter over the C12.18 protocol.  Returns
		True on success, False on a failure.  This can be called by modules
		in order to login with a username and password configured within
		the framework instance.
		"""
		username = self.options['USERNAME']
		userid = self.options['USERID']
		password = self.options['PASSWORD']
		if self.options['PASSWORDHEX']:
			hex_regex = re.compile('^([0-9a-fA-F]{2})+$')
			if hex_regex.match(password) == None:
				self.print_error('Invalid characters in password')
				raise FrameworkConfigurationError('invalid characters in password')
			password = unhexlify(password)
		if len(username) > 10:
			self.print_error('Username cannot be longer than 10 characters')
			raise FrameworkConfigurationError('username cannot be longer than 10 characters')
		if not (0 <= userid <= 0xffff):
			self.print_error('User id must be between 0 and 0xffff')
			raise FrameworkConfigurationError('user id must be between 0 and 0xffff')
		if len(password) > 20:
			self.print_error('Password cannot be longer than 20 characters')
			raise FrameworkConfigurationError('password cannot be longer than 20 characters')
		
		if not self.serial_connection.start():
			return False
		if not self.serial_connection.login(username, userid, password):
			return False
		return True
