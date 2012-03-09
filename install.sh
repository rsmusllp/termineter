#! /bin/sh
# Termineter Framework Convenience Install Script
# Copies all of the necessary files to the proper directories

USAGE="Termineter Framework Convenience Installer
Usage:

	install.sh [ path to install to ]

If a path is not specified /opt will be used."

if [ "$(id -u)" != "0" ]; then
	echo "This Must Be Run As Root"
	echo ""
	echo "$USAGE"
	exit 1
fi

if [ $# != 1 ]; then
	INSTALLROOT="/opt"
else
	INSTALLROOT="$1"
fi

if [ ! -d "$INSTALLROOT" ]; then
	echo "Invalid Directory"
	echo ""
	echo "$USAGE"
	exit 1
fi

EXEPATH="/usr/local/bin/termineter"
FRMWKBASE="$INSTALLROOT/termineter"

echo "Copying Files To: $FRMWKBASE"

if [ ! -d "$FRMWKBASE" ]; then
	mkdir $FRMWKBASE
fi
cp -r * $FRMWKBASE

echo "#/bin/sh" > $EXEPATH                                             
echo "FRMWKBASE=$INSTALLROOT/termineter" >> $EXEPATH
echo "python -B \$FRMWKBASE/termineter.py \"\$@\"" >> $EXEPATH
chmod +x $EXEPATH

echo "Done, Thanks For Playing."
