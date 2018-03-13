#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/__init__.py
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

from __future__ import unicode_literals

__version__ = '1.0.5'

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
