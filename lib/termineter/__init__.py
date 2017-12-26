#  termineter/__init__.py
#
#  Copyright 2016 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
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

__version__ = '1.0.0'

import os
import subprocess

import smoke_zephyr.utilities

def get_revision():
	"""
	Retrieve the current git revision identifier. If the git binary can not be
	found or the repository information is unavailable, None will be returned.

	:return: The git revision tag if it's available.
	:rtype: str
	"""
	git_bin = smoke_zephyr.utilities.which('git')
	if not git_bin:
		return None
	proc_h = subprocess.Popen(
		(git_bin, 'rev-parse', 'HEAD'),
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		close_fds=True,
		cwd=os.path.dirname(os.path.abspath(__file__))
	)
	rev = proc_h.stdout.read().strip()
	proc_h.wait()
	if not len(rev):
		return None
	return rev.decode('utf-8')

revision = get_revision()
