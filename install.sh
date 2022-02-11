#!/usr/bin/env bash
setupFile() {
	if [ -n "$G_VERSION" ]; then
		cat hls.plugin.in|sed s/XXXXX/$G_VERSION/g > hls.plugin
		cat hls_stack.plugin.in|sed s/XXXXX/$G_VERSION/g > hls_stack.plugin
	else
		cat hls_stack.plugin.in|sed s/XXXXX/42.0/g > hls_stack.plugin
	fi
}
installToLocal() {
	cp hls.{py,plugin} ~/.local/share/gnome-builder/plugins
	cp hls_stack.{py,plugin} ~/.local/share/gnome-builder/plugins
}
# The sed lines are from https://github.com/Prince781/vala-language-server/blob/master/plugins/gnome-builder/get_builder_abi.sh
if ! command -v gnome-builder &> /dev/null; then
	echo GNOME Builder not found as a normal installed package
	if [ $(flatpak list|grep org.gnome.Builder|wc -l) == "1" ]; then
		echo Found GNOME Builder as a flatpak
		export G_VERSION=$(flatpak run org.gnome.Builder --version | sed -nr '/GNOME Builder/ { s/GNOME Builder ([[:digit:]]+\.[[:digit:]]+).*$/\1/ p }')
		setupFile
		installToLocal
	else
		echo GNOME-Builder is not installed
		exit 1
	fi
else
	echo GNOME-Builder found as a normal installed package
	export G_VERSION=$(gnome-builder --version | sed -nr '/GNOME Builder/ { s/GNOME Builder ([[:digit:]]+\.[[:digit:]]+).*$/\1/ p }')
	setupFile
	installToLocal
fi
