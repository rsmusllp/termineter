#!/usr/bin/python
# -*- Mode: Python; py-indent-offset: 4 -*-
#
# Copyright (C) 2005, 2007  Ray Burr
# Copyright (C) 2016        Spencer McIntyre
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

# DISCLAIMER: I don't pretend to be a math wizard.  I don't have a
# deep understanding of all of the theory behind CRCs.  Part of the
# reason I originally wrote this is to help understand and verify CRC
# algorithms in practice.  It is likely that some of my terminology is
# inaccurate.

# Requires at least Python 2.7

"""
This module can model common CRC algorithms given the set of defining
parameters.  This is intended to be easy to use for experimentation
rather than optimized for speed.  It is slow even for a native Python
CRC implementation.

Several common CRC algorithms are predefined in this module.

:authors: Ray Burr, Spencer McIntyre
:license: MIT License
:contact: http://www.nightmare.com/~ryb/

Examples
========

  >>> str("{0:X}".format(CRC32.calc_string('123456789')))
  'CBF43926'

This test function runs all of the defined algorithms on the test
input string '123456789':

  >>> _print_results()
  CRC-5-USB: 19
  CRC-8-SMBUS: F4
  CRC-15: 059E
  CRC-16: BB3D
  CRC-16-USB: B4C8
  CRC-CCITT: 29B1
  CRC-HDLC: 906E
  CRC-24: 21CF02
  CRC-32: CBF43926
  CRC-32C: E3069283
  CRC-64: 46A5A9388A5BEFFE
  CRC-256: 79B96BDC0C519B239BE759EC0688C86FD25A3F4DF1E7F054AD1F923D0739DAC8

Calculating in parts:

  >>> value = CRC32.calc_string('1234')
  >>> str("{0:X}".format(CRC32.calc_string('56789', value)))
  'CBF43926'

Or, done a different way:

  >>> crc = CrcRegister(CRC32)
  >>> crc.take_string('1234')
  >>> crc.take_string('56789')
  >>> str("{0:X}".format(crc.get_final_value()))
  'CBF43926'

Inversion of a CRC function:

  >>> CRC_CCITT.reverse().reflect().calc_word(54321, 16, 0)
  1648
  >>> CRC_CCITT.calc_word(_, 16, 0)
  54321

A 15-bit CRC is used in CAN protocols.  The following sample CAN frame
(in binary here) is converted to hexadecimal for the calc_word call.
The bits after the 15-bit CRC are not included in the CRC::

  0 11101000001 0 0 0 0001 00010010 011000010111011 1 1 1 1111111

This sample CAN frame was found in this paper:
<http://www.anthony-marino.com/documents/HDL_implementation_CAN.pdf>

  >>> str("{0:X}".format(CRC15.calc_word(0x3A08112, 27)))
  '30BB'

If the CRC is included, the remainder should always be zero:

  >>> print(CRC15.calc_word(0x1D0408930BB, 42))
  0

A 5-bit CRC is used some kinds of USB packets.  Here is a sample
start-of-frame packet:

  10100101 01100111000 01111

(found at <http://www.nital.com/corporate/usb2snooper.html>)

The first field is the PID (not included in the CRC), the next 11-bit
field is the frame number (0xE6, LSb-first order), and the final five
bits are the CRC (0x1E, LSb-first order).

  >>> str("{0:X}".format(CRC5_USB.calc_word(0xE6, 11)))
  '1E'
"""

from __future__ import print_function
from __future__ import unicode_literals
import sys

# <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html>
__docformat__ = "restructuredtext en"

__version__ = "20160210"

class CrcAlgorithm(object):
    """
    Represents the parameters of a CRC algorithm.
    """

    # FIXME: Instances are supposed to be immutable, but attributes are
    # writable.

    def __init__(self, width, polynomial, name=None, seed=0, lsb_first=False, lsb_first_data=None, xor_mask=0):
        """
        :param width:

          The number of bits in the CRC register, or equivalently, the
          degree of the polynomial.

        :type width:

          an integer

        :param polynomial:

          The generator polynomial as a sequence of exponents

        :type polynomial:

          sequence or integer

        :param name:

          A name identifying algorithm.

        :type name:

          *str*

        :param seed:

          The initial value to load into the register.  (This is the
          value without *xor_mask* applied.)

        :type seed:

          an integer

        :param lsb_first:

          If ``true``, the register shifts toward the
          least-significant bit (sometimes called the *reflected* or
          *reversed* algorithim).  Otherwise, the register shifts
          toward the most-significant bit.

        :type lsb_first:

          *bool*

        :param lsb_first_data:

          If ``true``, input data is taken least-significant bit
          first.  Otherwise, data is taken most-significant bit first.
          If ``None`` or not given, the value of *lsb_first* is used.

        :type lsb_first_data:

          *bool*

        :param xor_mask:

          An integer mask indicating which bits should be inverted
          when returning the final result.  This is also used for the
          input value if provided.

        :type xor_mask:

          an integer
        """

        if width > 0:
            try:
                polymask = int(polynomial)
            except TypeError:
                # Guess it is already a sequence of exponents.
                polynomial = list(polynomial)
                polynomial.sort()
                polynomial.reverse()
                polynomial = tuple(polynomial)
            else:
                # Convert a mask to a tuple of exponents.
                if lsb_first:
                    polymask = reflect(polymask, width)
                polynomial = (width,)
                for i in range(width - 1, -1, -1):
                    if (polymask >> i) & 1:
                        polynomial += (i,)

            if polynomial[:1] != (width,):
                ValueError("mismatch between width and polynomial degree")

        self.width = width
        self.polynomial = polynomial
        self.name = name
        self.seed = seed
        self.lsb_first = lsb_first
        self.lsb_first_data = lsb_first_data
        self.xor_mask = xor_mask

        if not hasattr(width, "__rlshift__"):
            raise ValueError

        # FIXME: Need more checking of parameters.

    def __repr__(self):
        info = ""
        if self.name is not None:
            info = ' "%s"' % str(self.name)
        result = "<%s.%s%s @ %#x>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            info, id(self))
        return result

    def calc_bytes(self, s, value=None):
        """
        Calculate the CRC of the 8-bit bytes *s*.
        """
        r = CrcRegister(self, value)
        r.take_bytes(s)
        return r.get_final_value()

    def calc_string(self, s, value=None, encoding='utf-8'):
        s = s.encode(encoding)
        r = CrcRegister(self, value)
        r.take_string(s, encoding=encoding)
        return r.get_final_value()

    def calc_word(self, word, width, value=None):
        """
        Calculate the CRC of the integer *word* as a sequence of
        *width* bits.
        """
        r = CrcRegister(self, value)
        r.take_word(word, width)
        return r.get_final_value()

    def reflect(self):
        """
        Return the algorithm with the bit-order reversed.
        """
        ca = CrcAlgorithm(0, 0)
        ca._init_from_other(self)
        ca.lsb_first = not self.lsb_first
        if self.lsb_first_data is not None:
            ca.lsb_first_data = not self.lsb_first_data
        if ca.name:
            ca.name += " reflected"
        return ca

    def reverse(self):
        """
        Return the algorithm with the reverse polynomial.
        """
        ca = CrcAlgorithm(0, 0)
        ca._init_from_other(self)
        ca.polynomial = [(self.width - e) for e in self.polynomial]
        ca.polynomial.sort()
        ca.polynomial.reverse()
        ca.polynomial = tuple(ca.polynomial)
        if ca.name:
            ca.name += " reversed"
        return ca

    def _init_from_other(self, other):
        self.width = other.width
        self.polynomial = other.polynomial
        self.name = other.name
        self.seed = other.seed
        self.lsb_first = other.lsb_first
        self.lsb_first_data = other.lsb_first_data
        self.xor_mask = other.xor_mask


class CrcRegister(object):
    """
    Holds the intermediate state of the CRC algorithm.
    """

    def __init__(self, crc_algorithm, value=None):
        """
        :param crc_algorithm:

          The CRC algorithm to use.

        :type crc_algorithm:

          `CrcAlgorithm`

        :param value:

          The initial register value to use.  The result previous of a
          previous CRC calculation, can be used here to continue
          calculation with more data.  If this parameter is ``None``
          or not given, the register will be initialized with
          algorithm's default seed value.

        :type value:

          an integer
        """

        self.crc_algorithm = crc_algorithm
        p = crc_algorithm

        self.bit_mask = (1 << p.width) - 1

        word = 0
        for n in p.polynomial:
            word |= 1 << n
        self.poly_mask = word & self.bit_mask

        if p.lsb_first:
            self.poly_mask = reflect(self.poly_mask, p.width)

        if p.lsb_first:
            self.in_bit_mask = 1 << (p.width - 1)
            self.out_bit_mask = 1
        else:
            self.in_bit_mask = 1
            self.out_bit_mask = 1 << (p.width - 1)

        if p.lsb_first_data is not None:
            self.lsb_first_data = p.lsb_first_data
        else:
            self.lsb_first_data = p.lsb_first

        self.reset()

        if value is not None:
            self.value = value ^ p.xor_mask

    def __str__(self):
        return format_binary_string(self.value, self.crc_algorithm.width)

    def reset(self):
        """
        Reset the state of the register with the default seed value.
        """
        self.value = int(self.crc_algorithm.seed)

    def take_bit(self, bit):
        """
        Process a single input bit.
        """
        out_bit = ((self.value & self.out_bit_mask) != 0)
        if self.crc_algorithm.lsb_first:
            self.value >>= 1
        else:
            self.value <<= 1
        self.value &= self.bit_mask
        if out_bit ^ bool(bit):
            self.value ^= self.poly_mask

    def take_bytes(self, data):
        if sys.version_info[0] == 2:
            data = bytearray(data)
        for byte in data:
            self.take_word(byte)

    def take_word(self, word, width=8):
        """
        Process a binary input word.

        :param word:

          The input word.  Since this can be a Python ``long``, there
          is no coded limit to the number of bits the word can
          represent.

        :type word:

          an integer

        :param width:

          The number of bits *word* represents.

        :type width:

          an integer
        """
        if self.lsb_first_data:
            bit_list = range(0, width)
        else:
            bit_list = range(width - 1, -1, -1)
        for n in bit_list:
            self.take_bit((word >> n) & 1)

    def take_string(self, s, encoding='utf-8'):
        """
        Process a string as input.  It is handled as a sequence of
        8-bit integers.
        """
        if not isinstance(s, bytes):
            s = s.encode(encoding)
        return self.take_bytes(s)

    def get_value(self):
        """
        Return the current value of the register as an integer.
        """
        return self.value

    def get_final_value(self):
        """
        Return the current value of the register as an integer with
        *xor_mask* applied.  This can be used after all input data is
        processed to obtain the final result.
        """
        p = self.crc_algorithm
        return self.value ^ p.xor_mask


def reflect(value, width):
    return sum(
        ((value >> x) & 1) << (width - 1 - x)
        for x in range(width))

def format_binary_string(value, width):
    return "".join("01"[(value >> i) & 1] for i in range(width - 1, -1, -1))

# Some standard algorithms are defined here.  I believe I was able to
# verify the correctness of each of these in some way (against an
# existing implementation or sample data with a known result).

#: Same CRC algorithm as Python's zlib.crc32
CRC32 = CrcAlgorithm(
    name="CRC-32",
    width=32,
    polynomial=(32, 26, 23, 22, 16, 12, 11, 10, 8, 7, 5, 4, 2, 1, 0),
    seed=0xFFFFFFFF,
    lsb_first=True,
    xor_mask=0xFFFFFFFF
)

CRC16 = CrcAlgorithm(
    name="CRC-16",
    width=16,
    polynomial=(16, 15, 2, 0),
    seed=0x0000,
    lsb_first=True,
    xor_mask=0x0000
)

#: Used in USB data packets.
CRC16_USB = CrcAlgorithm(
    name="CRC-16-USB",
    width=16,
    polynomial=(16, 15, 2, 0),
    seed=0xFFFF,
    lsb_first=True,
    xor_mask=0xFFFF
)

CRC_CCITT = CrcAlgorithm(
    name="CRC-CCITT",
    width=16,
    polynomial=(16, 12, 5, 0),
    seed=0xFFFF,
    lsb_first=False,
    xor_mask=0x0000
)

#: This is the algorithm used in X.25 and for the HDLC 2-byte FCS.
CRC_HDLC = CrcAlgorithm(
    name="CRC-HDLC",
    width=16,
    polynomial=(16, 12, 5, 0),
    seed=0xFFFF,
    lsb_first=True,
    xor_mask=0xFFFF
)

#: Used in ATM HEC and SMBus.
CRC8_SMBUS = CrcAlgorithm(
    name="CRC-8-SMBUS",
    width=8,
    polynomial=(8, 2, 1, 0),
    seed=0,
    lsb_first=False,
    xor_mask=0
)

#: Used in RFC-2440 and MIL STD 188-184.
CRC24 = CrcAlgorithm(
    name="CRC-24",
    width=24,
    polynomial=(24, 23, 18, 17, 14, 11, 10, 7, 6, 5, 4, 3, 1, 0),
    seed=0xB704CE,
    lsb_first=False,
    xor_mask=0
)

#: Used in Controller Area Network frames.
CRC15 = CrcAlgorithm(
    name="CRC-15",
    width=15,
    polynomial=(15, 14, 10, 8, 7, 4, 3, 0),
    seed=0,
    lsb_first=False,
    xor_mask=0
)

#: Used in iSCSI (RFC-3385); usually credited to Guy Castagnoli.
CRC32C = CrcAlgorithm(
    name="CRC-32C",
    width=32,
    polynomial=(32, 28, 27, 26, 25, 23, 22, 20, 19, 18, 14, 13, 11, 10, 9, 8, 6, 0),
    seed=0xFFFFFFFF,
    lsb_first=True,
    xor_mask=0xFFFFFFFF
)

#: CRC used in USB Token and Start-Of-Frame packets
CRC5_USB = CrcAlgorithm(
    name="CRC-5-USB",
    width=5,
    polynomial=(5, 2, 0),
    seed=0x1F,
    lsb_first=True,
    xor_mask=0x1F
)

#: ISO 3309
CRC64 = CrcAlgorithm(
    name="CRC-64",
    width=64,
    polynomial=(64, 4, 3, 1, 0),
    seed=0,
    lsb_first=True,
    xor_mask=0
)

#: This is just to show off the ability to handle a very wide CRC.
# If this is a standard, I don't know where it is from.  I found the
# polynomial on a web page of an apparent Czech "Lady Killer"
# <http://www.volny.cz/lk77/crc256mmx/>.
CRC256 = CrcAlgorithm(
    name="CRC-256",
    width=256,
    polynomial=0x82E2443E6320383A20B8A2A0A1EA91A3CCA99A30C5205038349C82AAA3A8FD27,
    seed=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
    lsb_first=True,
    xor_mask=0
)

# For the following I haven't found complete information and/or have
# no way to verify the result.  I started with the list on Wikipedia
# <http://en.wikipedia.org/wiki/Cyclic_redundancy_check>.
#
#CRC4_ITU = CrcAlgorithm(
#    name         = "CRC-4-ITU",
#    width        = 4,
#    polynomial   = (4, 1, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)
#
#CRC5_ITU = CrcAlgorithm(
#    name         = "CRC-5-ITU",
#    width        = 5,
#    polynomial   = (5, 4, 2, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)
#
#CRC6_ITU = CrcAlgorithm(
#    name         = "CRC-6-ITU",
#    width        = 6,
#    polynomial   = (6, 1, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)
#
#CRC7 = CrcAlgorithm(
#    name         = "CRC-7",
#    width        = 7,
#    polynomial   = (7, 3, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)
#
#CRC8_CCITT = CrcAlgorithm(
#    name         = "CRC-8-CCITT",
#    width        = 8,
#    polynomial   = (8, 7, 3, 2, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)
#
#CRC8_DALLAS = CrcAlgorithm(
#    name         = "CRC-8-Dallas",
#    width        = 8,
#    polynomial   = (8, 5, 4, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)
#
#CRC8 = CrcAlgorithm(
#    name         = "CRC-8",
#    width        = 8,
#    polynomial   = (8, 7, 6, 4, 2, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)
#
#CRC8_J1850 = CrcAlgorithm(
#    name         = "CRC-8-J1850",
#    width        = 8,
#    polynomial   = (8, 4, 3, 2, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)
#
#CRC10 = CrcAlgorithm(
#    name         = "CRC-10",
#    width        = 10,
#    polynomial   = (10, 9, 5, 4, 1, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)
#
#CRC12 = CrcAlgorithm(
#    name         = "CRC-12",
#    width        = 12,
#    polynomial   = (12, 11, 3, 2, 1, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)
#
#CRC64_ECMA182 = CrcAlgorithm(
#    name         = "CRC-64-ECMA-182",
#    width        = 64,
#    polynomial   = (64, 62, 57, 55, 54, 53, 52, 47, 46, 45, 40, 39, 38, 37, 35, 33, 32, 31, 29, 27, 24, 23, 22, 21, 19, 17, 13, 12, 10, 9, 7, 4, 1, 0),
#    seed         = ?,
#    lsb_first     = ?,
#    xor_mask      = ?)

def _call_calc_string_123456789(v):
    return v.calc_string('123456789')

def _print_results(fn=_call_calc_string_123456789):
    d = sys.modules[__name__].__dict__
    algorithms = sorted(
        (v for (k, v) in d.items() if isinstance(v, CrcAlgorithm)),
        key=lambda v: (v.width, v.name))
    for a in algorithms:
        print(("{0}: {1:0" + str((a.width + 3) // 4) + "X}").format(a.name, fn(a)))

def _test():
    import doctest
    return doctest.testmod(sys.modules[__name__])

if __name__ == "__main__":
    _test()
