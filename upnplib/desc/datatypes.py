# MIT License
# 
# Copyright (c) 2022 MatrixEditor
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import dateutil.parser as dateparser
import urllib3.util as urlparser
import datetime

ui1 = int
"""Unsigned 1 Byte int. Same format as int without leading sign"""

ui2 = int
"""Unsigned 2 Byte int. Same format as int without leading sign."""

ui4 = int
"""Unsigned 4 Byte int. Same format as int without leading sign."""

ui8 = int
"""Unsigned 8 Byte int. Same format as int without leading sign."""

i1 = int
"""1 Byte int. Same format as int."""

i2 = int
"""2 Byte int. Same format as int."""

i4 = int
"""4 Byte int. Same format as int."""

i8 = int
"""8 Byte int. Same format as int."""

Int = int
"""Fixed point, integer number."""

r4 = float
"""
4 Byte float. Same format as float. shall be between 3.40282347E+38 to
1.17549435E-38
"""

r8 = float
"""
8 Byte float. Same format as float. shall be between - 1.79769313486232E308 
and -4.94065645841247E-324 for negative values and between 4.94065645841247E-324 
and 1.79769313486232E308 for positive values, i.e., IEEE 64-bit (8-Byte) double. 
"""

Number = float
"""Same as r8."""

Fixed_14_4 = float
"""
Same as r8 but no more than 14 digits to the left of the decimal point and no
more than 4 to the right.
"""

Float = float
"""Floating point number."""

char = int
"""Unicode string. One character long."""

String = str
"""Unicode string. No limit on length."""

Date = str
"""Date in a subset of ISO 8601 format without time data"""

DateTime = str
"""Date in ISO 8601 format with allowed time but no time zone."""

dateTime_tz = str
"""Date in ISO 8601 format with allowed time and allowed time zone."""

Time = str
"""Time in a subset of ISO 8601 format with no date and no time zone."""

time_tz = str
"""Time in a subset of ISO 8601 format with allowed time zone but no date."""

boolean = bool
"""
"0" for false or "1" for true. The values “true", “yes", “false", or "no" are
deprecated and shall not be sent but shall be accepted when received.
When received, the values "true" and "yes" shall be interpreted as true and
the values "false" and "no" shall be interpreted as false.
"""

Bin_base64 = str
"""
MIME-style Base64 encoded binary BLOB. Takes 3 Bytes, splits them into 4
parts, and maps each 6 bit piece to an octet. (3 octets are encoded as 4.)
No limit on size.
"""

Bin_hex = str
"""
Hexadecimal digits representing octets. Treats each nibble as a hex digit
and encodes as a separate Byte. (1 octet is encoded as 2.) No limit on size.
"""

Uri = str
"""Universal Resource Identifier."""

Uuid = str
"""
Universally Unique ID."""

INT_WRAPPER = lambda x: int(x)
FLOAT_WRAPPER = lambda x: int(x)
STR_WRAPPER = lambda x: x

def _parse_time(x):
  _date = dateparser.parse(x)
  if _date.tzinfo is None:
    return _date.time()
  else: return datetime.time(_date.hour, _date.minute, _date.second, _date.microsecond,
                             _date.tzinfo) 
__types__ = {
  'ui1': (ui1, INT_WRAPPER),
  'ui2': (ui2, INT_WRAPPER),
  'ui4': (ui4, INT_WRAPPER),
  'ui8': (ui8, INT_WRAPPER),
  'i1': (i1, INT_WRAPPER),
  'i2': (i2, INT_WRAPPER),
  'i4': (i4, INT_WRAPPER),
  'i8': (i8, INT_WRAPPER),
  'r4': (r4, FLOAT_WRAPPER),
  'r8': (r8, FLOAT_WRAPPER),
  'Number': (Number, FLOAT_WRAPPER),
  'boolean': (boolean, lambda x: x in ['true', 'yes', '1']),
  'Int': (Int, INT_WRAPPER),
  'Float': (Float, FLOAT_WRAPPER),
  'Bin_base64': (Bin_base64, STR_WRAPPER),
  'Bin_hex': (Bin_hex, STR_WRAPPER),
  'Uri': (Uri, lambda x: urlparser.parse_url(x)),
  'Uuid': (Uuid, STR_WRAPPER),
  'time_tz': (time_tz, _parse_time),
  'Time': (Time, _parse_time),
  'Date': (Date, lambda x: dateparser.parse(x).date()),
  'DateTime': (DateTime, dateparser.parse),
  'dateTime_tz': (dateTime_tz, dateparser.parse),
  'char': (char, STR_WRAPPER),
  'String': (String, STR_WRAPPER)
}

def unmarshal_str(typename: str, value: str):
  for name in __types__:
    if typename == name:
      value_wrapper = __types__[name][1]
      return value_wrapper(value)
