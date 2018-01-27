#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  termineter/modules/diff_tables.py
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
#  MA 02110-1301, USA.

from __future__ import unicode_literals

import binascii
import difflib

import c1219.constants
from termineter.module import TermineterModule

HTML_HEADER = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />
    <title>Diff Tables</title>
    <style type="text/css">
        table.diff {font-family:Courier; border:medium;}
        .diff_header {background-color:#e0e0e0}
        td.diff_header {text-align:right}
        .diff_highlight {background-color:#c0c0c0}
        .diff_ins {background-color:#aaffaa}
        .diff_rep {background-color:#ffff77}
        .diff_del {background-color:#ffaaaa}
    </style>
</head>

<body>
"""

HTML_TABLE_LEGEND = """
<table class="diff" summary="Legend">
    <tr><th> Legend </th></tr>
    <tr><td class="diff_ins">&nbsp;Added&nbsp;</td><td class="diff_rep">Changed</td><td class="diff_del">Deleted</td></tr>
</table>
"""

HTML_TABLE_HEADER = """<table class="diff" cellspacing="0" cellpadding="0" rules="groups" >
    <tr><td>Table Number</td><td>Table Data</td></tr>
"""

HTML_TABLE_FOOTER = """</table>
"""

HTML_FOOTER = """</body>
"""

class Module(TermineterModule):
	def __init__(self, *args, **kwargs):
		TermineterModule.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Check C12.19 Tables For Differences'
		self.detailed_description = 'This module will compare two CSV files created with dump_tables and display differences in a formatted HTML file.'
		self.options.add_string('FIRST_FILE', 'the first csv file to compare')
		self.options.add_string('SECOND_FILE', 'the second csv file to compare')
		self.options.add_string('REPORT_FILE', 'file to write the report data into', default='table_diff.html')
		self.advanced_options.add_boolean('ALL_TABLES', 'do not skip tables that typically change', default=False)

	def run(self):
		first_file = self.options['FIRST_FILE']
		first_file = open(first_file, 'r')
		second_file = self.options['SECOND_FILE']
		second_file = open(second_file, 'r')
		self.report = open(self.options['REPORT_FILE'], 'w', 1)
		self.differ = difflib.HtmlDiff()
		self.tables_to_skip = [
                    c1219.constants.PROC_INITIATE_TBL,
                    c1219.constants.PROC_RESPONSE_TBL,
                    c1219.constants.PRESENT_REGISTER_DATA_TBL
		]

		self.report.write(HTML_HEADER)
		self.report.write(HTML_TABLE_LEGEND)
		self.report.write('<br />\n')
		self.report.write(HTML_TABLE_HEADER)
		self.highlight_table = True

		self.frmwk.print_status('Generating Diff...')
		fid, fline = self.get_line(first_file)
		sid, sline = self.get_line(second_file)
		while fid is not None or sid is not None:
			if (fid is None or sid is None) or fid == sid:
				self.report_line(fline, sline, (fid or sid))
				fid, fline = self.get_line(first_file)
				sid, sline = self.get_line(second_file)
			elif fid < sid:
				self.report_line(fline, b'', fid)
				fid, fline = self.get_line(first_file)
			elif sid < fid:
				self.report_line(b'', sline, sid)
				sid, sline = self.get_line(second_file)

		self.report.write(HTML_TABLE_FOOTER)
		self.report.write(HTML_FOOTER)
		self.report.close()
		second_file.close()
		first_file.close()
		return

	def get_line(self, csv_file):
		line = csv_file.readline()
		if not line:
			return None, b''
		line = line.strip().split(',')
		if not line:
			return None, b''
		lid, ldata = int(line[0]), binascii.a2b_hex(line[-1])
		return lid, ldata

	def report_line(self, fline, sline, lineno):
		if not self.advanced_options['ALL_TABLES'] and lineno in self.tables_to_skip:
			return
		seq = difflib.SequenceMatcher(None, fline, sline)
		opcodes = seq.get_opcodes()
		if len(opcodes) > 1 or len(fline) != len(sline):
			lineno = "<b>{lineno}</b>".format(lineno=lineno)
		span_tag = "<span class=\"diff_{dtype}\">"
		row_header = "    <tr><td {highlight_table}>{lineno:<8}</td><td {highlight_row}nowrap=\"nowrap\">"
		if self.highlight_table:
			highlight_table = 'class="diff_highlight" '
		else:
			highlight_table = ''
		self.highlight_table = not self.highlight_table
		top_row = row_header.format(lineno=lineno, highlight_table=highlight_table, highlight_row='')
		bottom_row = row_header.format(lineno=lineno, highlight_table=highlight_table, highlight_row='class="diff_highlight" ')

		for tag, i1, i2, j1, j2 in opcodes:
			top_chunk = binascii.b2a_hex(fline[i1:i2]).decode('utf-8')
			bottom_chunk = binascii.b2a_hex(sline[j1:j2]).decode('utf-8')
			if tag != 'equal':
				top_row += span_tag.format(dtype=tag[:3])
				bottom_row += span_tag.format(dtype=tag[:3])
				while len(top_chunk) < len(bottom_chunk):
					top_chunk += ' '
				while len(bottom_chunk) < len(top_chunk):
					bottom_chunk += ' '
			top_row += top_chunk.replace(' ', '&nbsp;')
			bottom_row += bottom_chunk.replace(' ', '&nbsp;')
			if tag != 'equal':
				top_row += '</span>'
				bottom_row += '</span>'
		top_row += '</td></tr>'
		bottom_row += '</td></tr>'
		self.report.write(top_row + '\n')
		self.report.write(bottom_row + '\n')
