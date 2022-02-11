#!/usr/bin/env python3

#
# hls_stack.py
# Copyright 2022 JCWasmx86 <JCWasmx86@t-online.de>
#
# Based on: Stack_plugin.py
# Copyright 2018 Alberto Fanjul <albfan@gnome.org>
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

import threading
import os

from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Ide

_ = Ide.gettext

_ATTRIBUTES = ",".join([
	Gio.FILE_ATTRIBUTE_STANDARD_NAME,
	Gio.FILE_ATTRIBUTE_STANDARD_DISPLAY_NAME,
	Gio.FILE_ATTRIBUTE_STANDARD_SYMBOLIC_ICON,
])

class StackBuildSystemDiscovery(Ide.SimpleBuildSystemDiscovery):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.props.glob = "stack.yaml"
		self.props.hint = "hls_stack"
		self.props.priority = 2000

class StackBuildSystem(Ide.Object, Ide.BuildSystem):
	project_file = GObject.Property(type=Gio.File)

	def do_get_id(self):
		return "stack"

	def do_get_display_name(self):
		return "Stack"

	def do_get_priority(self):
		return 2000

class StackPipelineAddin(Ide.Object, Ide.PipelineAddin):
	"""
	The StackPipelineAddin is responsible for creating the necessary build
	stages and attaching them to phases of the build pipeline.
	"""

	def do_load(self, pipeline):
		context = self.get_context()
		build_system = Ide.BuildSystem.from_context(context)

		if type(build_system) != StackBuildSystem:
			return
		project_file = build_system.props.project_file
		project_dir = os.path.dirname(project_file.get_path())
		config = pipeline.get_config()
		builddir = pipeline.get_builddir()
		runtime = config.get_runtime()
		srcdir = pipeline.get_srcdir()

		build_launcher = pipeline.create_launcher()
		build_launcher.set_cwd(srcdir)
		new_path = os.path.expanduser("~/.ghcup/bin") + ":/app/bin/:/usr/bin/:" + os.getenv("PATH")
		build_launcher.setenv("PATH", new_path, True)
		build_launcher.push_argv(os.path.expanduser("~/.ghcup/bin/stack"))
		build_launcher.push_argv("build")

		clean_launcher = pipeline.create_launcher()
		clean_launcher.setenv("PATH", new_path, True)
		clean_launcher.set_cwd(srcdir)
		clean_launcher.push_argv(os.path.expanduser("~/.ghcup/bin/stack"))
		clean_launcher.push_argv("clean")

		build_stage = Ide.PipelineStageLauncher.new(context, build_launcher)
		build_stage.set_name(_("Building project"))
		build_stage.set_clean_launcher(clean_launcher)
		build_stage.connect("query", self._query)
		self.track(pipeline.attach(Ide.PipelinePhase.BUILD, 0, build_stage))



	def _query(self, stage, pipeline, targets, cancellable):
		stage.set_completed(False)

class StackBuildTarget(Ide.Object, Ide.BuildTarget):

	def do_get_install_directory(self):
		return None

	def do_get_name(self):
		return "stack-run"

	def do_get_language(self):
		return "haskell"

	def do_get_cwd(self):
		context = self.get_context()
		project_file = Ide.BuildSystem.from_context(context).project_file
		if project_file.query_file_type(0, None) == Gio.FileType.DIRECTORY:
			return project_file.get_path()
		else:
			return project_file.get_parent().get_path()

	def do_get_argv(self):
		return [os.path.expanduser("~/.ghcup/bin/stack"), "run"]

	def do_get_priority(self):
		return 0

class StackBuildTargetProvider(Ide.Object, Ide.BuildTargetProvider):

	def do_get_targets_async(self, cancellable, callback, data):
		task = Ide.Task.new(self, cancellable, callback)
		task.set_priority(GLib.PRIORITY_LOW)

		context = self.get_context()
		build_system = Ide.BuildSystem.from_context(context)

		if type(build_system) != StackBuildSystem:
			task.return_error(GLib.Error("Not stack build system", domain=GLib.quark_to_string(Gio.io_error_quark()), code=Gio.IOErrorEnum.NOT_SUPPORTED))
			return

		task.targets = [build_system.ensure_child_typed(StackBuildTarget)]
		task.return_boolean(True)

	def do_get_targets_finish(self, result):
		if result.propagate_boolean():
			return result.targets
