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

class FileWalker:
	def __init__(self, filespath):
		"""
		This class is used to easily iterate over files in a directory.
		
		@type filespath: string
		@param filespath: A path to either a file or a directory.  If a
		file is passed then that will be the only file returned during the
		iteration.  If a directory is passed, all files will be recursively
		returned during the iteration.
		"""
		self.filespath = filespath
		if os.path.isdir(self.filespath):
			self.__iter__= self.nextDir
		elif os.path.isfile(self.filespath):
			self.__iter__ = self.nextFile

	def nextDir(self):
		for root, subFolder, files in os.walk(self.filespath):
			for curFile in files:
				curFile = os.path.join(root, curFile)
				yield curFile
		raise StopIteration
	
	def nextFile(self):
		yield self.filespath
		raise StopIteration

class Namespace:
	"""
	This class is used to hold attributes of the framework.  It doesn't
	really do anything, it's used for organizational purposes only.
	"""
	pass
