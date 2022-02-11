#!/usr/bin/env python3

# hls.py
# Copyright 2022 JCWasmx86 <JCWasmx86@t-online.de>
#
# Based on: ts_language_server_plugin.py
# Copyright 2021 Georg Vienna <georg.vienna@himbarsoft.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import gi
import os

from gi.repository import GLib
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Ide


class HLSService(Ide.LspService):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.set_inherit_stderr(True)
		self.set_search_path([os.path.expanduser("~/.ghcup/bin")])
		self.set_program("haskell-language-server-wrapper")

	def do_configure_launcher(self, pipeline, launcher):
		launcher.push_argv("--lsp")
		launcher.push_argv("--debug")
		launcher.push_argv("--logfile")
		launcher.push_argv(os.path.expanduser("~/.cache") + "/hls.log")
		launcher.setenv("PATH", os.path.expanduser("~/.ghcup/bin") + ":" + "/app/bin/:/usr/bin/" + os.getenv("PATH"), True);

	def do_configure_client(self, client):
		client.add_language("haskell")


class HLSDiagnosticProvider(Ide.LspDiagnosticProvider, Ide.DiagnosticProvider):
	def do_load(self):
		HLSService.bind_client(self)

class HLSCompletionProvider(Ide.LspCompletionProvider, Ide.CompletionProvider):
	def do_load(self, context):
		HLSService.bind_client(self)

	def do_get_priority(self, context):
		return -1000

class HLSSymbolResolver(Ide.LspSymbolResolver, Ide.SymbolResolver):
	def do_load(self):
		HLSService.bind_client(self)

class HLSHighlighter(Ide.LspHighlighter, Ide.Highlighter):
	def do_load(self):
		HLSService.bind_client(self)

class HLSFormatter(Ide.LspFormatter, Ide.Formatter):
	def do_load(self):
		HLSService.bind_client(self)

class HLSHoverProvider(Ide.LspHoverProvider, Ide.HoverProvider):
	def do_prepare(self):
		self.props.category = "Haskell Language Server"
		self.props.priority = 200
		HLSService.bind_client(self)

class HLSRenameProvider(Ide.LspRenameProvider, Ide.RenameProvider):
	def do_load(self):
		HLSService.bind_client(self)

class HLSCodeActionProvider(Ide.LspCodeActionProvider, Ide.CodeActionProvider):
	def do_load(self):
		HLSService.bind_client(self)
