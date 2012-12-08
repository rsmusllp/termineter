#  framework/modules/set_meter_mode.py
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
from c1219.errors import C1219ProcedureError
from c1218.errors import C1218ReadTableError, C1218WriteTableError

class Module(optical_module_template):
	def __init__(self, *args, **kwargs):
		optical_module_template.__init__(self, *args, **kwargs)
		self.version = 1
		self.author = [ 'Spencer McIntyre <smcintyre@securestate.net>' ]
		self.description = 'Change the Meter\'s Operating Mode'
		self.detailed_description = 'Change the operating mode of the meter. Accepted values for MODE are METERING, TEST, METERSHOP, and FACTORY.'
		self.options.addString('MODE', 'the mode to set the meter to', True)
	
	def run(self):
		conn = self.frmwk.serial_connection
		logger = self.logger
		mode = self.options['MODE']
		mode = mode.upper()
		mode = mode.replace('_', '')
		mode = mode.replace(' ', '')
		if mode[-4:] == 'MODE':
			mode = mode[:-4]
		mode_dict = {'METERING':1, 'TEST':2, 'METERSHOP':4, 'FACTORY':8}
		if not mode in mode_dict:
			self.frmwk.print_error('unknown mode, please use METERING, TEST, METERSHOP, or FACTORY')
			return
		
		if not self.frmwk.serial_login():
			logger.warning('meter login failed')
			self.frmwk.print_error('Meter login failed, can not execute procedure')
			return
		
		logger.info('setting mode to: ' + mode)
		self.frmwk.print_status('Setting Mode To: ' + mode)
		
		mode = mode_dict[mode]
		errCode, data = None, ''
		try:
			errCode, data = conn.runProcedure(6, False, chr(mode))
			self.frmwk.print_good('Sucessfully Changed The Mode')
		except C1218ReadTableError as error:
			logger.error('caught ' + error.__class__.__name__ + ': ' + str(error))
			self.frmwk.print_error('Caught ' + error.__class__.__name__ + ': ' + str(error))
		except C1218WriteTableError as error:
			if error.errCode == 4:	# onp/operation not possible
				self.frmwk.print_error('Meter responded that it can not set the mode to the desired type')
			else:
				logger.error('caught ' + error.__class__.__name__ + ': ' + str(error))
				self.frmwk.print_error('Caught ' + error.__class__.__name__ + ': ' + str(error))
		except C1219ProcedureError as error:
			logger.error('caught ' + error.__class__.__name__ + ': ' + str(error))
			self.frmwk.print_error('Caught ' + error.__class__.__name__ + ': ' + str(error))
		conn.stop()
		return
