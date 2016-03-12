#  termineter/modules/diff_tables.py
#
#  Copyright 2013 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

from __future__ import unicode_literals

import binascii
import difflib

import c1219.constants
from termineter.templates import TermineterModule

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
		self.version = 1
		self.author = ['Spencer McIntyre']
		self.description = 'Check C12.19 Tables For Differences'
		self.detailed_description = 'This module will compare two CSV files created with dump_tables and display differences in a formatted HTML file.'
		self.options.add_string('FIRSTFILE', 'the first csv file to compare')
		self.options.add_string('SECONDFILE', 'the second csv file to compare')
		self.options.add_string('REPORTFILE', 'file to write the report data into', default='table_diff.html')
		self.advanced_options.add_boolean('ALLTABLES', 'do not skip tables that typically change', default=False)

	def run(self):
		first_file = self.options['FIRSTFILE']
		first_file = open(first_file, 'r')
		second_file = self.options['SECONDFILE']
		second_file = open(second_file, 'r')
		self.report = open(self.options['REPORTFILE'], 'w', 1)
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
		if not self.advanced_options['ALLTABLES'] and lineno in self.tables_to_skip:
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
