#  termineter/interface.py
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

from __future__ import absolute_import
from __future__ import unicode_literals

import code
import logging
import os
import platform
import random
import shlex
import subprocess
import sys
import textwrap

import termineter
import termineter.cmd
import termineter.core
import termineter.errors
import termineter.its

codename = 'T-900'

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
		intro += fmt_string.format(self.__name__, 'v' + termineter.__version__ + '') + os.linesep
		intro += fmt_string.format('model:', codename) + os.linesep
		intro += fmt_string.format('loaded modules:', len(self.frmwk.modules)) + os.linesep
		return intro

	@property
	def prompt(self):
		if self.frmwk.current_module:
			if self.frmwk.use_colors:
				return self.__name__ + ' (\033[1;33m' + self.frmwk.current_module.name + '\033[1;m) > '
			else:
				return self.__name__ + ' (' + self.frmwk.current_module.name + ') > '
		else:
			return self.__name__ + ' > '

	def run_rc_file(self, rc_file):
		if os.path.isfile(rc_file) and os.access(rc_file, os.R_OK):
			self.logger.info('processing "' + rc_file + '" for commands')
			for line in open(rc_file, 'r'):
				line = line.strip()
				if not len(line) or line[0] == '#':
					continue
				if line.startswith('print_'):
					line = line[6:]
					print_type, message = line.split(' ', 1)
					if print_type in ('error', 'good', 'line', 'status'):
						getattr(self, 'print_' + print_type)(message)
						continue
				self.print_line(self.prompt + line.strip())
				self.onecmd(line.strip())
		else:
			self.logger.error('invalid rc file: ' + rc_file)
			return False
		return True

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

	@termineter.cmd.command('Run the currently selected module')
	def do_exploit(self, args):
		self.do_run(args)

	def do_help(self, args):
		super(InteractiveInterpreter, self).do_help(args)
		self.print_line('')

	@termineter.cmd.command('Set and show logging options')
	@termineter.cmd.argument('action', choices=('set', 'show'), default='show', nargs='?', help='set or show the logging option')
	@termineter.cmd.argument('level', choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'), default='DEBUG', nargs='?', help='the logging level to set')
	def do_logging(self, args):
		if self.log_handler is None:
			self.print_error('No log handler is defined')
			return
		if args.action == 'show':
			loglvl = self.log_handler.level
			self.print_status('Effective logging level is: ' + ({10: 'DEBUG', 20: 'INFO', 30: 'WARNING', 40: 'ERROR', 50: 'CRITICAL'}.get(loglvl) or 'UNKNOWN'))
		elif args.action == 'set':
			new_lvl = args.level.upper()
			if new_lvl in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
				self.log_handler.setLevel(getattr(logging, new_lvl))
				self.print_status('Successfully changed the logging level to: ' + new_lvl)
			else:
				self.print_error('Missing log level, valid options are: debug, info, warning, error, critical')

	def complete_logging(self, text, line, begidx, endidx):
		return [i for i in ['set', 'show', 'debug', 'info', 'warning', 'error', 'critical'] if i.startswith(text.lower())]

	@termineter.cmd.command('Show module information')
	@termineter.cmd.argument('module', default=None, nargs='?', help='the module whose information is to be shown')
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
		self.print_line('     Name: ' + module.name)
		if len(module.author) == 1:
			self.print_line('   Author: ' + module.author[0])
		elif len(module.author) > 1:
			self.print_line('  Authors: ' + module.author[0])
			for additional_author in module.author[1:]:
				self.print_line('               ' + additional_author)
		self.print_line('  Version: ' + str(module.version))
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
			option_desc = module.options.get_option_help(option_name)
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

	@termineter.cmd.command('Reload a module into the framework')
	@termineter.cmd.argument('module', default=None, nargs='?', help='the module to reload')
	def do_reload(self, args):
		"""Reload a module in to the framework"""
		if args.module is not None:
			module_path = args.module
		elif self.frmwk.current_module:
			module_path = self.frmwk.current_module.path
		else:
			self.print_error('Must \'use\' module first')
			return

		if module_path not in self.frmwk.modules:
			self.print_error('Invalid Module Selected.')
			return
		try:
			module = self.frmwk.modules.reload(module_path)
		except termineter.errors.FrameworkRuntimeError:
			self.print_error('Failed to reload module')
			return
		if module_path == self.frmwk.current_module.name:
			self.frmwk.current_module = module
		self.print_status('Successfully reloaded module: ' + module_path)

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
	@termineter.cmd.argument('module', default=None, nargs='?', help='the module to run')
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
			try:
				options.set_option(args.option_name, args.option_value)
				self.print_line(args.option_name + ' => ' + args.option_value)
			except TypeError:
				self.print_error('Invalid data type')
			return
		elif args.option_name in advanced_options:
			try:
				advanced_options.set_option(args.option_name, args.option_value)
				self.print_line(args.option_name + ' => ' + args.option_value)
			except TypeError:
				self.print_error('Invalid data type')
			return
		self.print_error('Unknown variable name')

	def complete_set(self, text, line, begidx, endidx):
		if self.frmwk.current_module:
			options = self.frmwk.current_module.options
		else:
			options = self.frmwk.options
		return [i + ' ' for i in options.keys() if i.startswith(text.upper())]

	def do_show(self, args):
		"""Valid parameters for the "show" command are: modules, options"""
		args = shlex.split(args)
		if len(args) == 0:
			args.append('options')
		elif not args[0] in ['advanced', 'modules', 'options', '-h']:
			self.print_error('Invalid parameter "' + args[0] + '", use "show -h" for more information')
			return
		if args[0] == 'modules':
			self.print_line('')
			self.print_line('Modules' + os.linesep + '=======')
			self.print_line('')
			longest_name = 18
			for module_name in self.frmwk.modules.keys():
				longest_name = max(longest_name, len(module_name))
			fmt_string = "  {0:" + str(longest_name) + "} {1}"
			self.print_line(fmt_string.format('Name', 'Description'))
			self.print_line(fmt_string.format('----', '-----------'))
			module_names = sorted(list(self.frmwk.modules.keys()))
			module_names.sort()
			for module_name in module_names:
				module_obj = self.frmwk.modules[module_name]
				self.print_line(fmt_string.format(module_name, module_obj.description))
			self.print_line('')
			return
		elif args[0] == 'options' or args[0] == 'advanced':
			self.print_line('')
			if self.frmwk.current_module and args[0] == 'options':
				options = self.frmwk.current_module.options
				self.print_line('Module Options' + os.linesep + '==============')
			if self.frmwk.current_module and args[0] == 'advanced':
				options = self.frmwk.current_module.advanced_options
				self.print_line('Advanced Module Options' + os.linesep + '=======================')
			elif self.frmwk.current_module is None and args[0] == 'options':
				options = self.frmwk.options
				self.print_line('Framework Options' + os.linesep + '=================')
			elif self.frmwk.current_module is None and args[0] == 'advanced':
				options = self.frmwk.advanced_options
				self.print_line('Advanced Framework Options' + os.linesep + '==========================')
			self.print_line('')
			longest_name = 16
			longest_value = 10
			for option_name, option_def in options.items():
				longest_name = max(longest_name, len(option_name))
				longest_value = max(longest_value, len(str(options[option_name])))
			fmt_string = "  {0:<" + str(longest_name) + "} {1:<" + str(longest_value) + "} {2}"

			self.print_line(fmt_string.format('Name', 'Value', 'Description'))
			self.print_line(fmt_string.format('----', '-----', '-----------'))
			for option_name in options.keys():
				option_value = options[option_name]
				if option_value is None:
					option_value = ''
				option_desc = options.get_option_help(option_name)
				self.print_line(fmt_string.format(option_name, str(option_value), option_desc))
			self.print_line('')
		elif args[0] == '-h':
			self.print_status('Valid parameters for the "show" command are: modules, options')

	def complete_show(self, text, line, begidx, endidx):
		return [i for i in ['advanced', 'modules', 'options'] if i.startswith(text.lower())]

	@termineter.cmd.command('Select a module to use')
	@termineter.cmd.argument('module', default=None, help='the module to use')
	def do_use(self, args):
		if args.module not in self.frmwk.modules:
			self.logger.error('failed to change context to module: ' + args.module)
			self.print_error('Failed to change context to module: ' + args.module)
			return
		self.last_module = self.frmwk.current_module
		self.frmwk.current_module = self.frmwk.modules[args.module]

	def complete_use(self, text, line, begidx, endidx):
		return [i for i in self.frmwk.modules.keys() if i.startswith(text)]
