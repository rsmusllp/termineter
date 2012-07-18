#!/usr/bin/python -B
#
#  termineter.py
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
import logging
from argparse import ArgumentParser
from framework.interface import InteractiveInterpreter

__version__ = '0.1.0'

def main():
	parser = ArgumentParser(description = 'Termineter: Python Smart Meter Testing Framework', conflict_handler='resolve')
	parser.add_argument('-v', '--version', action = 'version', version = parser.prog + ' Version: ' + __version__)
	parser.add_argument('-L', '--log', dest = 'loglvl', action = 'store', choices = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default = 'CRITICAL', help = 'set the logging level')
	parser.add_argument('-r', '--rc-file', dest = 'resource_file', action = 'store', default = True, help = 'execute a resource file')
	arguments = parser.parse_args()
	logging.basicConfig(level = getattr(logging, arguments.loglvl), format = "%(levelname)-8s %(message)s")
	rc_file = arguments.resource_file
	del arguments, parser
	interpreter = InteractiveInterpreter(rc_file)
	interpreter.cmdloop()
	
if __name__ == '__main__':
	main()
