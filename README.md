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
communication over an optical interface.  Currently supported are Meters using
C1219-2007 with 7-bit character sets.  This is the most common configuration
found in North America.  Termineter communicates with Smart Meters via a
connection using an ANSI type-2 optical probe with a serial interface.

[![asciicast](https://asciinema.org/a/154407.png)][1]

# License
Termineter is released under the BSD 3-clause license, for more details see
the [LICENSE](https://github.com/securestate/termineter/blob/master/LICENSE) file.

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
Author: Spencer McIntyre - zeroSteiner ([\@zeroSteiner][2])

Author Home Page: http://www.securestate.com/

Project Home Page: https://github.com/securestate/termineter

Project Documentation: http://termineter.readthedocs.org/en/latest

# Install
Termineter can be installed from the Python Package Index using
pip. Simply run `sudo pip install termineter`.

For additional install information please see the INSTALL.md file.

[1]: https://asciinema.org/a/154407
[2]: https://twitter.com/zeroSteiner
