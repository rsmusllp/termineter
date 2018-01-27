#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/core.py
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

import binascii
import importlib
import logging
import logging.handlers
import os
import re
import sys

import c1218.connection
import c1218.errors
import termineter.module
import termineter.errors
import termineter.options
import termineter.utilities

import serial
import serial.serialutil
import tabulate
import termcolor

class Framework(object):
	"""
	This is the main instance of the framework.  It contains and
	manages the serial connection as well as all of the loaded
	modules.
	"""
	def __init__(self, stdout=None):
		self.__package__ = '.'.join(self.__module__.split('.')[:-1])
		package_path = importlib.import_module(self.__package__).__path__[0]  # that's some python black magic trickery for you
		if stdout is None:
			stdout = sys.stdout
		self.stdout = stdout
		self.logger = logging.getLogger('termineter.framework')

		self.directories = termineter.utilities.Namespace()
		self.directories.user_data = os.path.abspath(os.path.join(os.path.expanduser('~'), '.termineter'))
		self.directories.data_path = os.path.abspath(os.path.join(package_path, 'data'))
		if not os.path.isdir(self.directories.data_path):
			self.logger.critical('path to data not found')
			raise termineter.errors.FrameworkConfigurationError('path to data not found')
		if not os.path.isdir(self.directories.user_data):
			os.mkdir(self.directories.user_data)

		self.serial_connection = None
		self._serial_connected = False

		# setup logging stuff
		main_file_handler = logging.handlers.RotatingFileHandler(os.path.join(self.directories.user_data, self.__package__ + '.log'), maxBytes=262144, backupCount=5)
		main_file_handler.setLevel(logging.DEBUG)
		main_file_handler.setFormatter(logging.Formatter("%(asctime)s %(name)-50s %(levelname)-10s %(message)s"))
		logging.getLogger('').addHandler(main_file_handler)

		# setup and configure options
		# Whether or not these are 'required' is really enforced by the individual
		# modules get_missing_options method and by which options they require based
		# on their respective types.  See framework/templates.py for more info.
		self.options = termineter.options.Options(self.directories)
		self.options.add_boolean('USE_COLOR', 'enable color on the console interface', default=False)
		self.options.add_string('SERIAL_CONNECTION', 'serial connection string')
		self.options.add_string('USERNAME', 'serial username', default='0000')
		self.options.add_integer('USER_ID', 'serial user id', default=0)
		self.options.add_string('PASSWORD', 'serial c12.18 password', default='00000000000000000000')
		self.options.add_boolean('PASSWORD_HEX', 'if the password is in hex', default=True)
		self.advanced_options = termineter.options.AdvancedOptions(self.directories)
		self.advanced_options.add_boolean('AUTO_CONNECT', 'automatically handle connections for modules', default=True)
		self.advanced_options.add_boolean('CACHE_TABLES', 'cache certain read-only tables', default=True)
		self.advanced_options.set_callback('CACHE_TABLES', self._opt_callback_set_cache_tables)
		self.advanced_options.add_integer('C1218_MAX_PACKETS', 'c12.18 maximum packets for reassembly', default=2)
		self.advanced_options.add_integer('C1218_PACKET_SIZE', 'c12.18 maximum packet size', default=512)
		self.advanced_options.add_integer('SERIAL_BAUD_RATE', 'serial connection baud rate', default=9600)
		self.advanced_options.add_integer('SERIAL_BYTE_SIZE', 'serial connection byte size', default=serial.EIGHTBITS)
		self.advanced_options.add_integer('SERIAL_STOP_BITS', 'serial connection stop bits', default=serial.STOPBITS_ONE)
		self.advanced_options.add_string('TABLE_FORMAT', 'the format to print tables in', default='simple')
		self.advanced_options.set_callback('TABLE_FORMAT', self._opt_callback_set_table_format)
		if sys.platform.startswith('linux'):
			self.options.set_option_value('USE_COLOR', 'True')

		# start loading modules
		self.current_module = None
		self.modules = termineter.module.ManagerManager(self, [
			os.path.abspath(os.path.join(__file__, '..', 'modules')),
			os.path.abspath(os.path.join(self.directories.user_data, 'modules'))
		])
		self.logger.info("successfully loaded {0:,} modules into the framework".format(len(self.modules)))
		return

	def __repr__(self):
		return '<' + self.__class__.__name__ + ' Loaded Modules: ' + str(len(self.modules)) + ', Serial Connected: ' + str(self.is_serial_connected()) + ' >'

	def _opt_callback_set_cache_tables(self, policy, _):
		if self.is_serial_connected():
			self.serial_connection.set_table_cache_policy(policy)
		return True

	def _opt_callback_set_table_format(self, table_format, _):
		if table_format not in tabulate.tabulate_formats:
			self.print_error('TABLE_FORMAT must be one of: ' + ', '.join(tabulate.tabulate_formats))
			return False
		return True

	def _run_optical(self, module):
		if not self._serial_connected:
			self.print_error('The serial interface has not been connected')
			return False

		try:
			self.serial_get()
		except Exception as error:
			self.print_exception(error)
			return False

		ConnectionState = termineter.module.ConnectionState
		if not self.advanced_options['AUTO_CONNECT']:
			return True
		if module.connection_state == ConnectionState.none:
			return True

		try:
			self.serial_connect()
		except Exception as error:
			self.print_exception(error)
			return
		self.print_good('Successfully connected and the device is responding')
		if module.connection_state == ConnectionState.connected:
			return True

		if not self.serial_login():
			self.logger.warning('meter login failed, some tables may not be accessible')
		if module.connection_state == ConnectionState.authenticated:
			return True
		self.logger.warning('unknown optical connection state: ' + module.connection_state.name)
		return True

	def reload_module(self, module_path=None):
		"""
		Reloads a module into the framework.  If module_path is not
		specified, then the current_module variable is used.  Returns True
		on success, False on error.

		@type module_path: String
		@param module_path: The name of the module to reload
		"""
		if module_path is None:
			if self.current_module is not None:
				module_path = self.current_module.name
			else:
				self.logger.warning('must specify module if not module is currently being used')
				return False
		if module_path not in self.module:
			self.logger.error('invalid module requested for reload')
			raise termineter.errors.FrameworkRuntimeError('invalid module requested for reload')

		self.logger.info('reloading module: ' + module_path)
		module_instance = self.import_module(module_path, reload_module=True)
		if not isinstance(module_instance, termineter.module.TermineterModule):
			self.logger.error('module: ' + module_path + ' is not derived from the TermineterModule class')
			raise termineter.errors.FrameworkRuntimeError('module: ' + module_path + ' is not derived from the TermineterModule class')
		if not hasattr(module_instance, 'run'):
			self.logger.error('module: ' + module_path + ' has no run() method')
			raise termineter.errors.FrameworkRuntimeError('module: ' + module_path + ' has no run() method')
		if not isinstance(module_instance.options, termineter.options.Options) or not isinstance(module_instance.advanced_options, termineter.options.Options):
			self.logger.error('module: ' + module_path + ' options and advanced_options must be termineter.options.Options instances')
			raise termineter.errors.FrameworkRuntimeError('options and advanced_options must be termineter.options.Options instances')
		module_instance.name = module_path.split('/')[-1]
		module_instance.path = module_path
		self.modules[module_path] = module_instance
		if self.current_module is not None:
			if self.current_module.path == module_instance.path:
				self.current_module = module_instance
		return True

	def run(self, module=None):
		if not isinstance(module, termineter.module.TermineterModule) and not isinstance(self.current_module, termineter.module.TermineterModule):
			raise termineter.errors.FrameworkRuntimeError('either the module or the current_module must be sent')
		if module is None:
			module = self.current_module
		if isinstance(module, termineter.module.TermineterModuleOptical) and not self._run_optical(module):
			return
		self.logger.info('running module: ' + module.path)
		try:
			result = module.run()
		finally:
			if isinstance(module, termineter.module.TermineterModuleOptical) and self.serial_connection and self.advanced_options['AUTO_CONNECT']:
				self.serial_connection.stop()
		return result

	@property
	def use_colors(self):
		return self.options['USE_COLOR']

	@use_colors.setter
	def use_colors(self, value):
		self.options.set_option_value('USE_COLOR', str(value))

	def get_module_logger(self, name):
		"""
		This returns a logger for individual modules to allow them to be
		inherited from the framework and thus be named appropriately.

		@type name: String
		@param name: The name of the module requesting the logger
		"""
		return logging.getLogger('termineter.module.' + name)

	def import_module(self, module_path, reload_module=False):
		module = self.__package__ + '.modules.' + module_path.replace('/', '.')
		try:
			module = importlib.import_module(module)
			if reload_module:
				importlib.reload(module)
			module_instance = module.Module(self)
		except Exception:
			self.logger.error('failed to load module: ' + module_path, exc_info=True)
			raise termineter.errors.FrameworkRuntimeError('failed to load module: ' + module_path)
		return module_instance

	def print_exception(self, error):
		message = 'Caught ' + error.__class__.__name__ + ': ' + str(error)
		self.logger.error(message, exc_info=True)
		self.print_error(message)

	def print_error(self, message):
		prefix = '[-] '
		if self.options['USE_COLOR']:
			prefix = termcolor.colored(prefix, 'red', attrs=('bold',))
		self.stdout.write(prefix + (os.linesep + prefix).join(message.split(os.linesep)) + os.linesep)
		self.stdout.flush()

	def print_good(self, message):
		prefix = '[+] '
		if self.options['USE_COLOR']:
			prefix = termcolor.colored(prefix, 'green', attrs=('bold',))
		self.stdout.write(prefix + (os.linesep + prefix).join(message.split(os.linesep)) + os.linesep)
		self.stdout.flush()

	def print_hexdump(self, data):
		data_len = len(data)
		i = 0
		while i < data_len:
			self.stdout.write("{0:04x}    ".format(i))
			for j in range(16):
				if i + j < data_len:
					self.stdout.write("{0:02x} ".format(data[i + j]))
				else:
					self.stdout.write('   ')
				if j % 16 == 7:
					self.stdout.write(' ')
			self.stdout.write('   ')
			r = ''
			for j in data[i:i + 16]:
				if 32 < j < 128:
					r += chr(j)
				else:
					r += '.'
			self.stdout.write(r + os.linesep)
			i += 16
		self.stdout.flush()

	def print_line(self, message):
		self.stdout.write(message + os.linesep)
		self.stdout.flush()

	def print_status(self, message):
		prefix = '[*] '
		if self.options['USE_COLOR']:
			prefix = termcolor.colored(prefix, 'blue', attrs=('bold',))
		self.stdout.write(prefix + (os.linesep + prefix).join(message.split(os.linesep)) + os.linesep)
		self.stdout.flush()

	def print_table(self, table, headers=(), line_prefix=None, tablefmt=None):
		tablefmt = tablefmt or self.advanced_options['TABLE_FORMAT']
		text = tabulate.tabulate(table, headers=headers, tablefmt=tablefmt)
		if line_prefix:
			text = '\n'.join(line_prefix + line for line in text.split('\n'))
		self.print_line(text)

	def print_warning(self, message):
		prefix = '[!] '
		if self.options['USE_COLOR']:
			prefix = termcolor.colored(prefix, '', attrs=('bold',))
		self.stdout.write(prefix + (os.linesep + prefix).join(message.split(os.linesep)) + os.linesep)
		self.stdout.flush()

	def is_serial_connected(self):
		"""
		Returns True if the serial interface is connected.
		"""
		return self._serial_connected

	def serial_disconnect(self):
		"""
		Closes the serial connection to the meter and disconnects from the
		device.
		"""
		if self._serial_connected:
			try:
				self.serial_connection.close()
			except c1218.errors.C1218IOError as error:
				self.logger.error('caught C1218IOError: ' + str(error))
			except serial.serialutil.SerialException as error:
				self.logger.error('caught SerialException: ' + str(error))
			self._serial_connected = False
			self.logger.warning('the serial interface has been disconnected')
		return True

	def serial_get(self):
		"""
		Create the serial connection from the framework settings and return
		it, setting the framework instance in the process.
		"""
		frmwk_c1218_settings = {
			'nbrpkts': self.advanced_options['C1218_MAX_PACKETS'],
			'pktsize': self.advanced_options['C1218_PACKET_SIZE']
		}

		frmwk_serial_settings = termineter.utilities.get_default_serial_settings()
		frmwk_serial_settings['baudrate'] = self.advanced_options['SERIAL_BAUD_RATE']
		frmwk_serial_settings['bytesize'] = self.advanced_options['SERIAL_BYTE_SIZE']
		frmwk_serial_settings['stopbits'] = self.advanced_options['SERIAL_STOP_BITS']

		self.logger.info('opening serial device: ' + self.options['SERIAL_CONNECTION'])
		try:
			self.serial_connection = c1218.connection.Connection(self.options['SERIAL_CONNECTION'], c1218_settings=frmwk_c1218_settings, serial_settings=frmwk_serial_settings, enable_cache=self.advanced_options['CACHE_TABLES'])
		except Exception as error:
			self.logger.error('could not open the serial device')
			raise error
		return self.serial_connection

	def serial_connect(self):
		"""
		Connect to the serial device.
		"""
		self.serial_get()
		try:
			self.serial_connection.start()
		except c1218.errors.C1218IOError as error:
			self.logger.error('serial connection has been opened but the meter is unresponsive')
			raise error
		self._serial_connected = True
		return True

	def serial_login(self):
		"""
		Attempt to log into the meter over the C12.18 protocol. Returns True on success, False on a failure. This can be
		called by modules in order to login with a username and password configured within the framework instance.
		"""
		if not self._serial_connected:
			raise termineter.errors.FrameworkRuntimeError('the serial interface is disconnected')

		username = self.options['USERNAME']
		user_id = self.options['USER_ID']
		password = self.options['PASSWORD']
		if self.options['PASSWORD_HEX']:
			hex_regex = re.compile('^([0-9a-fA-F]{2})+$')
			if hex_regex.match(password) is None:
				self.print_error('Invalid characters in password')
				raise termineter.errors.FrameworkConfigurationError('invalid characters in password')
			password = binascii.a2b_hex(password)
		if len(username) > 10:
			self.print_error('Username cannot be longer than 10 characters')
			raise termineter.errors.FrameworkConfigurationError('username cannot be longer than 10 characters')
		if not (0 <= user_id <= 0xffff):
			self.print_error('User id must be between 0 and 0xffff')
			raise termineter.errors.FrameworkConfigurationError('user id must be between 0 and 0xffff')
		if len(password) > 20:
			self.print_error('Password cannot be longer than 20 characters')
			raise termineter.errors.FrameworkConfigurationError('password cannot be longer than 20 characters')

		if not self.serial_connection.login(username, user_id, password):
			return False
		return True

	def test_serial_connection(self):
		"""
		Connect to the serial device and then verifies that the meter is
		responding.  Once the serial device is open, this function attempts
		to retrieve the contents of table #0 (GEN_CONFIG_TBL) to configure
		the endianess it will use.  Returns True on success.
		"""
		self.serial_connect()

		username = self.options['USERNAME']
		user_id = self.options['USER_ID']
		if len(username) > 10:
			self.logger.error('username cannot be longer than 10 characters')
			raise termineter.errors.FrameworkConfigurationError('username cannot be longer than 10 characters')
		if not (0 <= user_id <= 0xffff):
			self.logger.error('user id must be between 0 and 0xffff')
			raise termineter.errors.FrameworkConfigurationError('user id must be between 0 and 0xffff')

		try:
			if not self.serial_connection.login(username, user_id):
				self.logger.error('the meter has rejected the username and user id')
				raise termineter.errors.FrameworkConfigurationError('the meter has rejected the username and user id')
		except c1218.errors.C1218IOError as error:
			self.logger.error('serial connection has been opened but the meter is unresponsive')
			raise error

		try:
			general_config_table = self.serial_connection.get_table_data(0)
		except c1218.errors.C1218ReadTableError as error:
			self.logger.error('serial connection as been opened but the general configuration table (table #0) could not be read')
			raise error

		if general_config_table[0] & 1:
			self.logger.info('setting the connection to use big-endian for C12.19 data')
			self.serial_connection.c1219_endian = '>'
		else:
			self.logger.info('setting the connection to use little-endian for C12.19 data')
			self.serial_connection.c1219_endian = '<'

		try:
			self.serial_connection.stop()
		except c1218.errors.C1218IOError as error:
			self.logger.error('serial connection has been opened but the meter is unresponsive')
			raise error

		self.logger.warning('the serial interface has been connected')
		return True
