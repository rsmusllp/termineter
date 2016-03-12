# Termineter Install Guide
## Requirements
Termineter supports Python 2.7 and 3.4+. It is recommended that
users use Python3.
The requirements are listed in the requirements.txt file. They can
be installed with `python3 -m pip install -r requirements.txt`.

## How To Install Termineter
No installation or modification is necessary.  Start a command
prompt, navigate to the termineter directory and use python to run
termineter.

If using a USB optical probe with an FTDI chip, you may need to load
and configure the appropriate serial to USB driver in order to use
the device. The following command will configure the hardware on
Linux.

**Kernel version < 3.12**
```
modprobe ftdi-sio vendor=0xVVVV product=0xPPPP
```

**Kernel version >= 3.12**
```
modprobe ftdi-sio
echo VVVV PPPP > /sys/bus/usb-serial/drivers/ftdi_sio/new_id
```

Where VVVV is the vendor ID and PPPP is the product ID.  These
values can be obtained from the lsusb command.

# How To Update (All)
Updates can be obtained from the projects home page, either in
source archives for major revisions or from the trunk.  Git must be
installed and used to update to the latest revision from the trunk.
