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

from framework.templates import module_template
from binascii import unhexlify
from time import sleep
import os
import re

class Module(module_template):
	def __init__(self, *args, **kwargs):
		module_template.__init__(self, *args, **kwargs)
		self.version = 2
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Brute Force Credentials'
		self.detailed_description = 'This module is used for brute forcing credentials on the smart meter.  Passwords are not limited to ASCII values and in order to test the entire character space the user will have to provide a dictionary of hex strings and set USEHEX to true.'
		self.options.addBoolean('USEHEX', 'values in word list are in hex', default = True)
		self.options.addRFile('DICTIONARY', 'dictionary of passwords to try', required = True, default = '$DATA_PATH smeter_passwords.txt')
		self.options.addString('USERNAME', 'user name to attempt to log in as', default = '0000')
		self.options.addInteger('USERID', 'user id to attempt to log in as', default = 1)
		self.advanced_options.addBoolean('STOPONSUCCESS', 'stop after the first successful login', default = True)
		self.advanced_options.addFloat('DELAY', 'time in seconds to wait between attempts', default = 0.20)
	
	def run(self, frmwk):
		conn = frmwk.serial_connection
		usehex = self.options.getOptionValue('USEHEX')
		dictionary_path = self.options.getOptionValue('DICTIONARY')
		username = self.options.getOptionValue('USERNAME')
		userid = self.options.getOptionValue('USERID')
		logger = frmwk.get_module_logger(self.name)
		time_delay = self.advanced_options.getOptionValue('DELAY')
		
		if len(username) > 10:
			frmwk.print_error('Username cannot be longer than 10 characters')
			return
		if not (0 <= userid <= 0xffff):
			frmwk.print_error('User id must be between 0 and 0xffff')
			return
		if not os.path.isfile(dictionary_path):
			frmwk.print_error('Can not find dictionary path')
			return
		
		password_list = open(dictionary_path, 'r')
		hex_regex = re.compile('^([0-9a-fA-F]{2})+$')
		
		frmwk.print_status('Starting brute force')
		
		password = password_list.readline()
		while password:
			if usehex:
				password = password.strip()
				if hex_regex.match(password) == None:
					logger.error('invalid characters found while searching for hex')
					frmwk.print_error('Invalid characters found while searching for hex')
					password_list.close()
					return
				password = unhexlify(password)
			else:
				password = password.rstrip()
			if len(password) > 20:
				if usehex:
					logger.warning('skipping password: ' + password.encode('hex') + ' due to length (can not be exceed 20 bytes)')
				else:
					logger.warning('skipping password: ' + password + ' due to length (can not be exceed 20 bytes)')
				password = password_list.readline()
				continue
			while not conn.start():
				sleep(time_delay)
			sleep(time_delay)
			if conn.login(username, userid, password):
				if usehex:
					frmwk.print_good('Successfully logged in. Username: ' + username + ' Userid: ' + str(userid) + ' Password: ' + password.encode('hex'))
				else:
					frmwk.print_good('Successfully logged in. Username: ' + username + ' Userid: ' + str(userid) + ' Password: ' + password)
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
			password = password_list.readline()
		password_list.close()
