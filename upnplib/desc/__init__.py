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
__doc__ = """
The upnplib.desc module covers all classes and interfaces in relation to 
IPnP capable network devices, such as service control presentation descriptions
as well as the defined actions and variables.
"""

from . import datatypes as xmltype

from .urnobj import (
  urntype,
  urn
)

def typeof(typename: str) -> type:
  for _type in xmltype.__types__:
    if _type.lower().replace('_', '.') == typename:
      return xmltype.__types__[_type][0]

from .upnpdev import *
from .scpd import *

__all__ = [
  'xmltype', 'urn', 'urntype', 'typeof',
  'direction', 'StateVariable', 'Argument',
  'Action', 'scpd', 'Icon', 'Service', 
  'ServiceList', 'device', 'new_device'
]