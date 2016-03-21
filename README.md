```
   ______                    _            __
  /_  __/__  _________ ___  (_)___  ___  / /____  _____
   / / / _ \/ ___/ __ `__ \/ / __ \/ _ \/ __/ _ \/ ___/
  / / /  __/ /  / / / / / / / / / /  __/ /_/  __/ /
 /_/  \___/_/  /_/ /_/ /_/_/_/ /_/\___/\__/\___/_/

```

# Summary
Termineter is a Python framework which provides a platform for the security
testing of smart meters.  It implements the C1218 and C1219 protocols for
communication over an optical interface.  Currently supportted are Meters using
C1219-2007 with 7-bit character sets.  This is the most common configuration
found in North America.  Termineter communicates with Smart Meters via a
connection using an ANSI type-2 optical probe with a serial interface.

# License
Copyright (C) 2011-2016, Spencer J. McIntyre

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.

This license does not apply to the following components:

* CrcMoose

# Credits
Special Thanks To:

* Caroline Aronoff (Alpha testing and fixing older PySerial compatibility)
* Chris Murrey - f8lerror (Alpha testing)
* Jake Garlie - jagar (Alpha testing)
* Scott Turner - fantomgoat (Bug report and fix)
* Kevin Underwood (Bug report and fix)
* Don Weber - cutaway (Developer of InGuardians' OptiGuard)

Termineter Development Team:

* Spencer McIntyre of the SecureState Research and Innovation Team

# About
Author: Spencer McIntyre - [zeroSteiner](https://twitter.com/zeroSteiner)

Author Home Page: http://www.securestate.com/

Project Home Page: https://github.com/securestate/termineter

Project Documentation: http://termineter.readthedocs.org/en/latest

# Install
Termineter can be installed from the Python Package Index using
pip. Simply run `sudo pip install termineter`.

For additional install information please see the INSTALL.md file.
