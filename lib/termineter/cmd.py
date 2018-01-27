#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/cmd.py
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

import argparse
import cmd
import logging
import shlex
import socket
import ssl
import sys

class ArgumentParser(argparse.ArgumentParser):
	def __init__(self, *args, **kwargs):
		self.stdout = kwargs.pop('stdout', sys.stdout)
		super(ArgumentParser, self).__init__(*args, **kwargs)

	def error(self, message):
		self.print_usage()
		self.exit(2, "{}: error: {}\n".format(self.prog, message))

	def exit(self, status=0, message=None):
		if message:
			self.stdout.write(message)
		raise ArgumentParserExit(status=status, message=message)

	def print_help(self):
		return super(ArgumentParser, self).print_help(file=self.stdout)

	def print_usage(self):
		return super(ArgumentParser, self).print_usage(file=self.stdout)

class ArgumentParserExit(Exception):
	def __init__(self, status=0, message=None):
		self.status = status
		self.message = message

class _Command(object):
	def __init__(self, callback, name=None):
		self._arguments = []
		self.callback = callback
		name = name or callback.__name__[3:]  # remove the do_ prefix
		self.parser = ArgumentParser(prog=name)

	def _wrapper(self, inst, args):
		parser = self.parser
		try:
			args = shlex.split(args)
		except ValueError as error:
			message = 'Failed to parse argument'
			if error.args:
				message += ' (' + error.args[0] + ')'
			inst.stdout.write(message + '\n')
			return
		parser.stdout = inst.stdout
		try:
			args = parser.parse_args(args)
		except ArgumentParserExit:
			return
		return self.callback(inst, args)

	def add_argument(self, *args, **kwargs):
		self._arguments.append((args, kwargs))

	@property
	def wrapper(self):
		self._arguments.reverse()
		for args, kwargs in self._arguments:
			self.parser.add_argument(*args, **kwargs)

		def wrapper_function(*args, **kwargs):
			return self._wrapper(*args, **kwargs)
		wrapper_function.__doc__ = self.parser.format_help()
		return wrapper_function

def argument(*args, **kwargs):
	def decorator(command):
		if not isinstance(command, _Command):
			command = _Command(command)
		command.add_argument(*args, **kwargs)
		return command
	return decorator

def command(description=None):
	def decorator(command):
		if not isinstance(command, _Command):
			command = _Command(command)
		command.parser.description = description
		return command.wrapper
	return decorator

def epilog(text):
	def decorator(command):
		if not isinstance(command, _Command):
			command = _Command(command)
		command.parser.epilog = text
		return command
	return decorator

class Cmd(cmd.Cmd):
	def __init__(self, stdin=None, stdout=None, **kwargs):
		super(Cmd, self).__init__(stdin=stdin, stdout=stdout, **kwargs)
		if stdin is not None:
			self.use_rawinput = False
		self._hidden_commands = ['EOF']
		self._disabled_commands = []
		self.__package__ = '.'.join(self.__module__.split('.')[:-1])

	def cmdloop(self):
		while True:
			try:
				super(Cmd, self).cmdloop()
				return
			except KeyboardInterrupt:
				self.print_line('')
				self.print_error('Please use the \'exit\' command to quit')
				continue

	def get_names(self):
		commands = super(Cmd, self).get_names()
		for name in self._hidden_commands:
			if 'do_' + name in commands:
				commands.remove('do_' + name)
		for name in self._disabled_commands:
			if 'do_' + name in commands:
				commands.remove('do_' + name)
		return commands

	def emptyline(self):
		# don't do anything on a blank line being passed
		pass

	def help_help(self):  # Get help out of the undocumented section, stupid python
		self.do_help('')

	def precmd(self, line):  # use this to allow using '?' after the command for help
		tmp_line = line.split()
		if not tmp_line:
			return line
		if tmp_line[0] in self._disabled_commands:
			self.default(tmp_line[0])
			return ''
		if len(tmp_line) == 1:
			return line
		if tmp_line[1] == '?':
			self.do_help(tmp_line[0])
			return ''
		return line

	def do_exit(self, args):
		return True

	def do_EOF(self, args):
		"""Exit The Interpreter"""
		self.print_line('')
		return self.do_exit('')

	def run_rc_file(self, rc_file):
		for line in open(rc_file, 'r'):
			line = line.strip()
			if not len(line) or line[0] == '#':
				continue
			self.print_line(self.prompt + line.strip())
			self.onecmd(line.strip())
		return True

	@classmethod
	def serve(cls, addr, run_once=False, log_level=None, use_ssl=False, ssl_cert=None, init_kwargs=None):
		init_kwargs = init_kwargs or {}
		__package__ = '.'.join(cls.__module__.split('.')[:-1])
		logger = logging.getLogger(__package__ + '.interpreter.server')

		srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		srv_sock.bind(addr)
		logger.debug('listening for connections on: ' + addr[0] + ':' + str(addr[1]))
		srv_sock.listen(1)
		while True:
			try:
				(clt_sock, clt_addr) = srv_sock.accept()
			except KeyboardInterrupt:
				break
			logger.info('received connection from: ' + clt_addr[0] + ':' + str(clt_addr[1]))

			if use_ssl:
				ssl_sock = ssl.wrap_socket(clt_sock, server_side=True, certfile=ssl_cert)
				ins = ssl_sock.makefile('r', 1)
				outs = ssl_sock.makefile('w', 1)
			else:
				ins = clt_sock.makefile('r', 1)
				outs = clt_sock.makefile('w', 1)

			log_stream = logging.StreamHandler(outs)
			if log_level is not None:
				log_stream.setLevel(log_level)
			log_stream.setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))
			logging.getLogger('').addHandler(log_stream)

			interpreter = cls(stdin=ins, stdout=outs, **init_kwargs)
			try:
				interpreter.cmdloop()
			except socket.error:
				log_stream.close()
				logging.getLogger('').removeHandler(log_stream)
				logger.warning('received a socket error during the main interpreter loop')
				continue
			log_stream.flush()
			log_stream.close()
			logging.getLogger('').removeHandler(log_stream)

			outs.close()
			ins.close()
			clt_sock.shutdown(socket.SHUT_RDWR)
			clt_sock.close()
			del clt_sock
			if run_once:
				break
		srv_sock.shutdown(socket.SHUT_RDWR)
		srv_sock.close()
