#  c1218/utils.py
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

from struct import pack, unpack
import string
from binascii import hexlify, unhexlify
import CrcMoose # Get it from: http://www.nightmare.com/~ryb/code/CrcMoose.py

crc = CrcMoose.CRC_HDLC.calcString
crc_str = lambda x: pack("<H", crc(x))

def data_chksum(data):
	chksum = 0
	for i in unpack('B' * len(data), data):
		chksum += i
	return (((chksum - 1) & 0xff) ^ 0xff)

data_chksum_str = lambda x: chr(data_chksum(x))

def unit_tests():
	from c1218.data import Packet, Logon, Security, Write
	import sys
	while True:
		sys.stdout.write('[*] Testing c1218.Packet(\'\\x20\') ')
		sys.stdout.flush()
		if str(Packet('\x20')).encode('hex') == 'ee0000000001201310':
			sys.stdout.write(' PASSED\n')
			sys.stdout.flush()

		sys.stdout.write('[*] Testing c1218.Packet(\'\\x00\') ')
		sys.stdout.flush()
		if str(Packet('\x00')).encode('hex') == 'ee0000000001001131':
			sys.stdout.write(' PASSED\n')
			sys.stdout.flush()

		sys.stdout.write('[*] Testing c1218.Packet(c1218.Logon(\'Admin\', 1)) ')
		sys.stdout.flush()
		if str(Packet(Logon('Admin', 1))).encode('hex') == 'ee000000000d50000141646d696e20202020209fc9':
			sys.stdout.write(' PASSED\n')
			sys.stdout.flush()

		sys.stdout.write('[*] Testing c1218.Packet(c1218.Security(\'Password1\')) ')
		sys.stdout.flush()
		if str(Packet(Security('Password1'))).encode('hex') == 'ee00000000155150617373776f72643120202020202020202020202397':
			sys.stdout.write(' PASSED\n')
			sys.stdout.flush()

		sys.stdout.write('[*] Testing c1218.Packet(c1218.Write(1, 1, \'data data data\')) ')
		sys.stdout.flush()
		if str(Packet(Write(1, 'data data data', 1))).encode('hex') == 'ee00000000174f0001000001000e6461746120646174612064617461f28ee1':
			sys.stdout.write(' PASSED\n')
			sys.stdout.flush()
		return True
	sys.stdout.write(' FAILED\n')
	sys.stdout.flush()
	return False

def find_strings(data, minchars = 4):
	rstrings = []
	myprintables = string.ascii_letters + string.digits + string.punctuation + '\n\t\r '
	start = None
	for p in xrange(0, len(data)):
		if data[p] in myprintables:
			if start == None:
				start = p
		elif start != None:
			if (p - start) >= minchars:
				rstrings.append(data[start:p])
			start = None
	if start != None and ((p + 1) - start) >= minchars:
		rstrings.append(data[start:p + 1])
	return rstrings
