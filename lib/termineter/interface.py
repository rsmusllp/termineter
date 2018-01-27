#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/interface.py
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

from __future__ import absolute_import
from __future__ import unicode_literals

import code
import logging
import os
import platform
import random
import subprocess
import sys
import textwrap

import termineter
import termineter.cmd
import termineter.core
import termineter.errors
import termineter.its

import termcolor

codename = 'T-1000'

def complete_all_paths(path):
	if not path:
		return [(p + os.sep if os.path.isdir(p) else p) for p in os.listdir('.')]
	if path[-1] == os.sep and not os.path.isdir(path):
		return []
	if os.path.isdir(path):
		file_prefix = ''
	else:
		path, file_prefix = os.path.split(path)
		path = path or '.' + os.sep
	if not path[-1] == os.sep:
		path += os.sep
	return [path + (p + os.sep if os.path.isdir(os.path.join(path, p)) else p) for p in os.listdir(path) if p.startswith(file_prefix)]

def complete_path(path, allow_files=False):
	paths = complete_all_paths(path)
	if not allow_files:
		paths = [p for p in paths if not os.path.isfile(p)]
	return paths

# the core interpreter for the console
class InteractiveInterpreter(termineter.cmd.Cmd):
	"""The core interpreter for the CLI interface."""
	__name__ = 'termineter'
	prompt = __name__ + ' > '
	ruler = '+'
	doc_header = 'Type help <command> For Information\nList Of Available Commands:'
	def __init__(self, check_rc_file=True, stdin=None, stdout=None, log_handler=None):
		super(InteractiveInterpreter, self).__init__(stdin=stdin, stdout=stdout)
		if not self.use_rawinput:
			# No 'use_rawinput' will cause problems with the ipy command so disable it for now
			self._disabled_commands.append('ipy')

		if not termineter.its.on_linux:
			self._hidden_commands.append('prep_driver')
		self._hidden_commands.append('cd')
		self._hidden_commands.append('exploit')
		self._hidden_commands.append('print_status')
		self.last_module = None
		self.log_handler = log_handler
		if self.log_handler is None:
			self._disabled_commands.append('logging')
		self.logger = logging.getLogger('termineter.interpreter')
		self.frmwk = termineter.core.Framework(stdout=stdout)
		self.print_exception = self.frmwk.print_exception
		self.print_error = self.frmwk.print_error
		self.print_good = self.frmwk.print_good
		self.print_line = self.frmwk.print_line
		self.print_status = self.frmwk.print_status

		if check_rc_file:
			check_rc_file = os.path.join(self.frmwk.directories.user_data, 'console.rc')
			if os.path.isfile(check_rc_file) and os.access(check_rc_file, os.R_OK):
				self.print_status('Running commands from resource file: ' + check_rc_file)
				self.run_rc_file(check_rc_file)
		elif isinstance(check_rc_file, str):
			if os.path.isfile(check_rc_file) and os.access(check_rc_file, os.R_OK):
				self.print_status('Running commands from resource file: ' + check_rc_file)
				self.run_rc_file(check_rc_file)
			else:
				self.logger.error('could not access resource file: ' + check_rc_file)
				self.print_error('Could not access resource file: ' + check_rc_file)
		try:
			import readline
			readline.read_history_file(self.frmwk.directories.user_data + 'history.txt')
			readline.set_completer_delims(readline.get_completer_delims().replace('/', ''))
		except (ImportError, IOError):
			pass

	@property
	def intro(self):
		intro = os.linesep
		intro += '   ______              _          __         ' + os.linesep
		intro += '  /_  __/__ ______ _  (_)__  ___ / /____ ____' + os.linesep
		intro += '   / / / -_) __/  \' \/ / _ \/ -_) __/ -_) __/' + os.linesep
		intro += '  /_/  \__/_/ /_/_/_/_/_//_/\__/\__/\__/_/   ' + os.linesep
		intro += os.linesep
		fmt_string = "  <[ {0:<18} {1:>18}"
		intro += fmt_string.format(self.__name__, 'v' + termineter.__version__) + os.linesep
		intro += fmt_string.format('model:', codename) + os.linesep
		intro += fmt_string.format('loaded modules:', len(self.frmwk.modules)) + os.linesep
		return intro

	@property
	def prompt(self):
		if self.frmwk.current_module:
			module_name = self.frmwk.current_module.name
			if self.frmwk.use_colors:
				module_name = termcolor.colored(module_name, 'yellow', attrs=('bold',))
			return self.__name__ + ' (' + module_name + ') > '
		else:
			return self.__name__ + ' > '

	def reload_module(self, module):
		is_current = self.frmwk.current_module and module.path == self.frmwk.current_module.path
		try:
			module = self.frmwk.modules.reload(module.path)
		except termineter.errors.FrameworkRuntimeError:
			self.print_error('Failed to reload the module')
			return
		except Exception as error:
			self.print_exception(error)
			return
		self.print_status('Successfully reloaded module: ' + module.path)
		if is_current:
			self.frmwk.current_module = module
		return module

	def run_rc_file(self, rc_file):
		self.logger.info('processing "' + rc_file + '" for commands')
		return super(InteractiveInterpreter, self).run_rc_file(rc_file)

	@classmethod
	def serve(cls, *args, **kwargs):
		init_kwargs = kwargs.pop('init_kwargs', {})
		init_kwargs['check_rc_file'] = False
		kwargs['init_kwargs'] = init_kwargs
		super(InteractiveInterpreter, cls).serve(*args, **kwargs)

	@termineter.cmd.command('Stop using a module and return back to the framework context.')
	def do_back(self, args):
		self.frmwk.current_module = None

	@termineter.cmd.command('Display the banner')
	def do_banner(self, args):
		self.print_line(self.intro)

	@termineter.cmd.command('Change the current working directory.')
	@termineter.cmd.argument('path', help='the new path to change into')
	def do_cd(self, args):
		if not args.path:
			self.print_error('must specify a path')
			return
		if not os.path.isdir(args.path):
			self.print_error('invalid path')
			return
		os.chdir(args.path)

	def complete_cd(self, text, line, begidx, endidx):
		return complete_path(text, allow_files=False)

	@termineter.cmd.command('Connect the serial interface.')
	def do_connect(self, args):
		if self.frmwk.is_serial_connected():
			self.print_status('Already connected')
			return
		missing_options = self.frmwk.options.get_missing_options()
		if missing_options:
			self.print_error('The following options must be set: ' + ', '.join(missing_options))
			return
		try:
			self.frmwk.test_serial_connection()
		except Exception as error:
			self.print_exception(error)
			return
		self.print_good('Successfully connected and the device is responding')

	@termineter.cmd.command('Exit the interpreter.')
	def do_exit(self, args):
		quotes = (
			'I\'ll be back.',
			'Hasta la vista, baby.',
			'Come with me if you want to live.',
			'Where\'s John Connor?'
		)
		self.logger.info('received exit command, now exiting')
		self.print_status(random.choice(quotes))
		try:
			import readline
			readline.write_history_file(self.frmwk.directories.user_data + 'history.txt')
		except (ImportError, IOError):
			pass
		return True

	def do_exploit(self, args):
		"""Alias of the 'run' command"""
		self.do_run(args)

	def do_help(self, args):
		super(InteractiveInterpreter, self).do_help(args)
		self.print_line('')

	@termineter.cmd.command('Set and show logging options')
	@termineter.cmd.argument('level', nargs='?', help='the logging level to set')
	def do_logging(self, args):
		if self.log_handler is None:
			self.print_error('No log handler is defined')
			return
		if args.level is None:
			loglvl = self.log_handler.level
			self.print_status('Effective logging level is: ' + ({10: 'DEBUG', 20: 'INFO', 30: 'WARNING', 40: 'ERROR', 50: 'CRITICAL'}.get(loglvl) or 'UNKNOWN'))
			return

		new_level = args.level.upper()
		new_level = next((level for level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') if level.startswith(new_level)), None)
		if new_level is None:
			self.print_error('Invalid logging level: ' + args.level)
		self.log_handler.setLevel(getattr(logging, new_level))
		self.print_status('Successfully changed the logging level to: ' + new_level)

	def complete_logging(self, text, line, begidx, endidx):
		return [i for i in ['debug', 'info', 'warning', 'error', 'critical'] if i.startswith(text.lower())]

	@termineter.cmd.command('Show module information')
	@termineter.cmd.argument('module', nargs='?', help='the module whose information is to be shown')
	def do_info(self, args):
		if args.module is None:
			if self.frmwk.current_module is None:
				self.print_error('Must select module to show information')
				return
			module = self.frmwk.current_module
		elif args.module in self.frmwk.modules:
			module = self.frmwk.modules[args.module]
		else:
			self.print_error('Invalid module name')
			return

		self.print_line('')
		self.print_line('        Name: ' + module.name)
		if len(module.author) == 1:
			self.print_line('      Author: ' + module.author[0])
		elif len(module.author) > 1:
			self.print_line('     Authors: ' + module.author[0])
			for additional_author in module.author[1:]:
				self.print_line('              ' + additional_author)
		if isinstance(module, termineter.module.TermineterModuleOptical):
			self.print_line('  Connection: ' + module.connection_state.name)
		self.print_line('')
		self.print_line('Basic Options: ')
		longest_name = 16
		longest_value = 10
		for option_name, option_def in module.options.items():
			longest_name = max(longest_name, len(option_name))
			longest_value = max(longest_value, len(str(module.options[option_name])))
		fmt_string = "  {0:<" + str(longest_name) + "} {1:<" + str(longest_value) + "} {2}"
		self.print_line(fmt_string.format('Name', 'Value', 'Description'))
		self.print_line(fmt_string.format('----', '-----', '-----------'))
		for option_name in module.options.keys():
			option_value = module.options[option_name]
			if option_value is None:
				option_value = ''
			option_desc = module.options.get_option(option_name).help
			self.print_line(fmt_string.format(option_name, str(option_value), option_desc))
		self.print_line('')
		self.print_line('Description:')
		for line in textwrap.wrap(textwrap.dedent(module.detailed_description), 78):
			self.print_line('  ' + line)
		self.print_line('')

	def complete_info(self, text, line, begidx, endidx):
		return [i for i in self.frmwk.modules.keys() if i.startswith(text)]

	@termineter.cmd.command('Start an interactive Python interpreter')
	def do_ipy(self, args):
		"""Start an interactive Python interpreter"""
		import c1218.data
		import c1219.data
		from c1219.access.general import C1219GeneralAccess
		from c1219.access.security import C1219SecurityAccess
		from c1219.access.log import C1219LogAccess
		from c1219.access.telephone import C1219TelephoneAccess
		vars = {
			'termineter.__version__': termineter.__version__,
			'C1218Packet': c1218.data.C1218Packet,
			'C1218ReadRequest': c1218.data.C1218ReadRequest,
			'C1218WriteRequest': c1218.data.C1218WriteRequest,
			'C1219ProcedureInit': c1219.data.C1219ProcedureInit,
			'C1219GeneralAccess': C1219GeneralAccess,
			'C1219SecurityAccess': C1219SecurityAccess,
			'C1219LogAccess': C1219LogAccess,
			'C1219TelephoneAccess': C1219TelephoneAccess,
			'frmwk': self.frmwk,
			'os': os,
			'sys': sys
		}
		banner = 'Python ' + sys.version + ' on ' + sys.platform + os.linesep
		banner += os.linesep
		banner += 'The framework instance is in the \'frmwk\' variable.'
		if self.frmwk.is_serial_connected():
			vars['conn'] = self.frmwk.serial_connection
			banner += os.linesep
			banner += 'The connection instance is in the \'conn\' variable.'
		try:
			import IPython.terminal.embed
		except ImportError:
			pyconsole = code.InteractiveConsole(vars)
			savestdin = os.dup(sys.stdin.fileno())
			savestdout = os.dup(sys.stdout.fileno())
			savestderr = os.dup(sys.stderr.fileno())
			try:
				pyconsole.interact(banner)
			except SystemExit:
				sys.stdin = os.fdopen(savestdin, 'r', 0)
				sys.stdout = os.fdopen(savestdout, 'w', 0)
				sys.stderr = os.fdopen(savestderr, 'w', 0)
		else:
			self.print_line(banner)
			pyconsole = IPython.terminal.embed.InteractiveShellEmbed(
				ipython_dir=os.path.join(self.frmwk.directories.user_data, 'ipython')
			)
			pyconsole.mainloop(vars)

	@termineter.cmd.command('Prepare the optical probe driver')
	@termineter.cmd.argument('vendor_id', help='the 4 hex digits of the vendor id')
	@termineter.cmd.argument('product_id', help='the 4 hex digits of the product id')
	def do_prep_driver(self, args):
		if os.getuid():
			self.print_error('Must be running as root to prep the driver')
			return
		vendor_id = args.vendor_id
		if vendor_id.startswith('0x'):
			vendor_id = vendor_id[2:]
		product_id = args.product_id
		if product_id.startswith('0x'):
			product_id = product_id[2:]
		linux_kernel_version = platform.uname()[2].split('.')[:2]
		linux_kernel_version = tuple(int(part) for part in linux_kernel_version)
		if linux_kernel_version < (3, 12):
			proc_args = ['modprobe', 'ftdi-sio', "vendor=0x{0}".format(vendor_id), "product=0x{0}".format(product_id)]
		else:
			proc_args = ['modprobe', 'ftdi-sio']
		proc_h = subprocess.Popen(proc_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True, shell=False)
		if proc_h.wait():
			self.print_error('modprobe exited with a non-zero status code')
			return
		if linux_kernel_version >= (3, 12) and os.path.isfile('/sys/bus/usb-serial/drivers/ftdi_sio/new_id'):
			with open('/sys/bus/usb-serial/drivers/ftdi_sio/new_id', 'w') as file_h:
				file_h.write("{0} {1}".format(vendor_id, product_id))
		self.print_status('Finished driver preparation')

	@termineter.cmd.command('Use the last specified module.')
	def do_previous(self, args):
		if self.last_module is None:
			self.frmwk.print_error('no module has been previously selected')
			return
		self.frmwk.current_module, self.last_module = self.last_module, self.frmwk.current_module

	@termineter.cmd.command('Print a message in the interface.')
	@termineter.cmd.argument('message', help='the message to print')
	def do_print_status(self, args):
		self.print_status(args.message)

	@termineter.cmd.command('Load the protocon engine')
	@termineter.cmd.argument('-u', '--url', help='the connection URL (defaults to the serial device)')
	@termineter.cmd.argument('scripts', metavar='script', nargs='*', help='the script to execute')
	def do_protocon(self, args):
		try:
			import protocon
		except ImportError:
			self.print_error('The protocon package is unavailable, please install it first')
			return
		if args.url:
			url = args.url
		else:
			url = "serial://{0}?baudrate={1}&bytesize={2}&parity=N&stopbits={3}".format(
				self.frmwk.options['SERIAL_CONNECTION'],
				self.frmwk.advanced_options['SERIAL_BAUD_RATE'],
				self.frmwk.advanced_options['SERIAL_BYTE_SIZE'],
				self.frmwk.advanced_options['SERIAL_STOP_BITS']
			)
		try:
			engine = protocon.Engine.from_url(url)
		except protocon.ProtoconDriverError as error:
			self.print_error('Driver error: ' + error.message)
		except Exception as error:
			self.print_exception(error)
		else:
			engine.entry(args.scripts)
			engine.connection.close()
		return 0

	@termineter.cmd.command('Reload a module into the framework')
	@termineter.cmd.argument('module', nargs='?', help='the module to reload')
	def do_reload(self, args):
		"""Reload a module in to the framework"""
		if args.module is not None:
			if args.module not in self.frmwk.modules:
				self.print_error('Invalid Module Selected.')
				return
			module = self.frmwk.modules[args.module]
		elif self.frmwk.current_module:
			module = self.frmwk.current_module
		else:
			self.print_error('Must \'use\' module first')
			return
		self.reload_module(module)

	def complete_reload(self, text, line, begidx, endidx):
		return [i for i in self.frmwk.modules.keys() if i.startswith(text)]

	@termineter.cmd.command('Run one or more resource files')
	@termineter.cmd.argument('resource_files', metavar='resource_file', nargs='+', help='the resource files to run')
	def do_resource(self, args):
		for rc_file in args.resource_files:
			if not os.path.isfile(rc_file):
				self.print_error('Invalid resource file: ' + rc_file + ' (not found)')
				continue
			if not os.access(rc_file, os.R_OK):
				self.print_error('Invalid resource file: ' + rc_file + ' (no read permissions)')
				continue
			self.print_status('Running commands from resource file: ' + rc_file)
			self.run_rc_file(rc_file)

	def complete_resource(self, text, line, begidx, endidx):
		return complete_path(text, allow_files=True)

	@termineter.cmd.command('Run the specified module')
	@termineter.cmd.argument('-r', '--reload', action='store_true', default=False, help='reload the module before running it')
	@termineter.cmd.argument('module', nargs='?', help='the module to run')
	def do_run(self, args):
		old_module = None
		if args.module is None:
			if self.frmwk.current_module is None:
				self.print_error('Must \'use\' module first')
				return
		else:
			if args.module not in self.frmwk.modules:
				self.print_error('Invalid module specified: ' + args.module)
				return
			old_module = self.frmwk.current_module
			self.frmwk.current_module = self.frmwk.modules[args.module]
		module = self.frmwk.current_module
		if args.reload:
			module = self.reload_module(module)
			if module is None:
				return

		missing_options = module.get_missing_options()
		if missing_options:
			self.print_error('The following options must be set: ' + ', '.join(missing_options))
			return
		del missing_options

		try:
			self.frmwk.run()
		except KeyboardInterrupt:
			self.print_line('')
		except Exception as error:
			self.print_exception(error)
			old_module = None
		if old_module:
			self.frmwk.current_module = old_module

	def complete_run(self, text, line, begidx, endidx):
		return [i for i in self.frmwk.modules.keys() if i.startswith(text)]

	@termineter.cmd.command('Set an option\'s value')
	@termineter.cmd.argument('option_name', metavar='option', help='the option\'s name')
	@termineter.cmd.argument('option_value', metavar='value', help='the option\'s new value')
	def do_set(self, args):
		if self.frmwk.current_module:
			options = self.frmwk.current_module.options
			advanced_options = self.frmwk.current_module.advanced_options
		else:
			options = self.frmwk.options
			advanced_options = self.frmwk.advanced_options
		if args.option_name in options:
			pass
		elif args.option_name in advanced_options:
			options = advanced_options
		else:
			self.print_error('Unknown option: ' + args.option_name)
			return
		try:
			success = options.set_option_value(args.option_name, args.option_value)
		except TypeError:
			self.print_error('Invalid data type')
			return
		if success:
			self.print_line(args.option_name + ' => ' + args.option_value)

	def complete_set(self, text, line, begidx, endidx):
		if self.frmwk.current_module:
			options = self.frmwk.current_module.options
		else:
			options = self.frmwk.options
		return [i + ' ' for i in options.keys() if i.startswith(text.upper())]

	@termineter.cmd.command('Show the specified information')
	@termineter.cmd.argument('thing', choices=('advanced', 'modules', 'options'), default='options', nargs='?', help='what to show')
	def do_show(self, args):
		"""Valid parameters for the "show" command are: modules, options"""
		self.print_line('')
		if args.thing == 'modules':
			self.print_line('Modules' + os.linesep + '=======')
			headers = ('Name', 'Description')
			rows = [(module.path, module.description) for module in self.frmwk.modules.values()]
		else:
			if self.frmwk.current_module and args.thing == 'options':
				options = self.frmwk.current_module.options
				self.print_line('Module Options' + os.linesep + '==============')
			if self.frmwk.current_module and args.thing == 'advanced':
				options = self.frmwk.current_module.advanced_options
				self.print_line('Advanced Module Options' + os.linesep + '=======================')
			elif self.frmwk.current_module is None and args.thing == 'options':
				options = self.frmwk.options
				self.print_line('Framework Options' + os.linesep + '=================')
			elif self.frmwk.current_module is None and args.thing == 'advanced':
				options = self.frmwk.advanced_options
				self.print_line('Advanced Framework Options' + os.linesep + '==========================')
			headers = ('Name', 'Value', 'Description')
			raw_options = [options.get_option(name) for name in options]
			rows = [(option.name, str(option.value), option.help) for option in raw_options]
		rows = sorted(rows, key=lambda row: row[0])
		self.print_line('')
		self.frmwk.print_table(rows, headers=headers, line_prefix='  ')
		self.print_line('')
		return

	def complete_show(self, text, line, begidx, endidx):
		return [i for i in ['advanced', 'modules', 'options'] if i.startswith(text.lower())]

	@termineter.cmd.command('Select a module to use')
	@termineter.cmd.argument('module', help='the module to use')
	def do_use(self, args):
		if args.module not in self.frmwk.modules:
			self.logger.error('failed to change context to module: ' + args.module)
			self.print_error('Failed to change context to module: ' + args.module)
			return
		self.last_module = self.frmwk.current_module
		self.frmwk.current_module = self.frmwk.modules[args.module]

	def complete_use(self, text, line, begidx, endidx):
		return [i for i in self.frmwk.modules.keys() if i.startswith(text)]

	@termineter.cmd.command('Show the framework version information')
	def do_version(self, args):
		fmt_string = "{0:<18} {1:>24}"
		self.print_line(fmt_string.format(self.__name__ + ':', 'v' + termineter.__version__))
		revision = ('unknown' if termineter.revision is None else termineter.revision[:12])
		self.print_line(fmt_string.format('revision:', revision))
		self.print_line(fmt_string.format('model:', codename))
		self.print_line(fmt_string.format('loaded modules:', len(self.frmwk.modules)))
