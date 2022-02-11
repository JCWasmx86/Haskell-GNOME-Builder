#!/usr/bin/env bash
setupFile() {
	if [ -n "$G_VERSION" ]; then
		cat hls.plugin.in|sed s/XXXXX/$G_VERSION/g > hls.plugin
	else
		cat hls.plugin.in|sed s/XXXXX/42.0/g > hls.plugin
	fi
}
installToFlatpak() {
	echo After each upgrade you have to rerun this install script
	cp hls.{py,plugin} $(flatpak info org.gnome.Builder --show-location)/files/lib/gnome-builder/plugins/
}
installToLocal() {
	cp hls.{py,plugin} ~/.local/share/gnome-builder/plugins
}
# The sed lines are from https://github.com/Prince781/vala-language-server/blob/master/plugins/gnome-builder/get_builder_abi.sh
if ! command -v gnome-builder &> /dev/null; then
	echo GNOME Builder not found as a normal installed package
	if [ $(flatpak list|grep org.gnome.Builder|wc -l) == "1" ]; then
		echo Found GNOME Builder as a flatpak
		export G_VERSION=$(flatpak run org.gnome.Builder --version | sed -nr '/GNOME Builder/ { s/GNOME Builder ([[:digit:]]+\.[[:digit:]]+).*$/\1/ p }')
		setupFile
		installToFlatpak
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
