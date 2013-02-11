#  framework/utils.py
#  
#  Copyright 2012 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
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
import copy
import serial
import itertools

DEFAULT_SERIAL_SETTINGS = {
	'parity': serial.PARITY_NONE,
	'baudrate': 9600,
	'bytesize': serial.EIGHTBITS,
	'xonxoff': False,
	'interCharTimeout': None,
	'rtscts': False,
	'timeout': 1,
	'stopbits': serial.STOPBITS_ONE,
	'dsrdtr': False,
	'writeTimeout': None
}

def GetDefaultSerialSettings():
	return copy.copy(DEFAULT_SERIAL_SETTINGS)

class FileWalker:
	def __init__(self, filespath, absolute_path = False, skip_files = False, skip_dirs = False, filter_func = None):
		"""
		This class is used to easily iterate over files in a directory.
		
		@type filespath: string
		@param filespath: A path to either a file or a directory.  If a
		file is passed then that will be the only file returned during the
		iteration.  If a directory is passed, all files will be recursively
		returned during the iteration.
		
		@type absolute_path: boolean
		@param absolute_path: Whether or not the absolute path or a relative
		path should be returned.
		
		@type skip_files: boolean
		@param skip_files: Whether or not to skip files.
		
		@type skip_dirs: boolean
		@param skip_dirs: Whether or not to skip directories.
		
		@type filter_func: function
		@param filter_func: If defined, the filter_func function will be called
		for each file and if the function returns false the file will be
		skipped.
		"""
		if not (os.path.isfile(filespath) or os.path.isdir(filespath)):
			raise Exception(filespath + ' is neither a file or directory')
		if absolute_path:
			self.filespath = os.path.abspath(filespath)
		else:
			self.filespath = os.path.relpath(filespath)
		self.skip_files = skip_files
		self.skip_dirs = skip_dirs
		self.filter_func = filter_func
		if os.path.isdir(self.filespath):
			self.__iter__= self.nextDir
		elif os.path.isfile(self.filespath):
			self.__iter__ = self.nextFile

	def skip(self, curFile):
		if self.skip_files and os.path.isfile(curFile):
			return True
		if self.skip_dirs and os.path.isdir(curFile):
			return True
		if self.filter_func != None:
			if not self.filter_func(curFile):
				return True
		return False

	def nextDir(self):
		for root, dirs, files in os.walk(self.filespath):
			for curFile in files:
				curFile = os.path.join(root, curFile)
				if not self.skip(curFile):
					yield curFile
			for curDir in dirs:
				curDir = os.path.join(root, curDir)
				if not self.skip(curDir):
					yield curDir
		raise StopIteration
	
	def nextFile(self):
		if not self.skip(self.filespath):
			yield self.filespath
		raise StopIteration

class Namespace:
	"""
	This class is used to hold attributes of the framework.  It doesn't
	really do anything, it's used for organizational purposes only.
	"""
	pass

def unique(seq, idfunc = None): 
	"""
	Unique a list or tuple and preserve the order
	
	@type idfunc: Function or None
	@param idfunc: If idfunc is provided it will be called during the
	comparison process.
	"""
	if idfunc is None:
		idfunc = lambda x: x
	preserved_type = type(seq)
	seen = {}
	result = []
	for item in seq:
		marker = idfunc(item)
		if marker in seen:
			continue
		seen[marker] = 1
		result.append(item)
	return preserved_type(result)

class StringGenerator:
	def __init__(self, startlen, endlen = None, charset = None):
		"""
		This class is used to generate raw strings for bruteforcing.
		
		@type startlen: Integer
		@param startlen: The minimum size of the string to bruteforce.
		
		@type endlen: Integer
		@param endlen: The maximum size of the string to bruteforce.
		
		@type charset: String, Tuple or None
		@param charset: the character set to use while generating the 
		strings.  If None, the full binary space will be used (0 - 255).
		"""
		self.startlen = startlen
		if endlen == None:
			self.endlen = startlen
		else:
			self.endlen = endlen
		if charset == None:
			charset = map(chr, range(0, 256))
		elif type(charset) == str:
			charset = list(charset)
		charset = unique(charset)
		charset.sort()
		self.charset = tuple(charset)
	
	def __iter__(self):
		length = self.startlen
		while (length <= self.endlen):
			for string in itertools.product(self.charset, repeat = length):
				yield ''.join(string)
			length += 1
		raise StopIteration
