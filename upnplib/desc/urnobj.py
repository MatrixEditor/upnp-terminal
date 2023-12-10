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

from enum import Enum

class urntype(Enum):
  DEVICE = 'device'
  SERVICE = 'service'
  SERVICE_ID = 'serviceId'

class urn:
  """UPnP device/service type. Single URI.

  This class beahves barely like a string. Use str(urn_obj) or repr(urn_obj) to 
  retrieve the full urn value.

  Specification taken from UPnP-Architecture:

  For standard devices defined by a UPnP Forum working committee, shall begin with
  "urn:schemas-upnp-org:device:" followed by the standardized device type suffix, a colon,
  and an integer device version i.e. urn:schemas-upnp-org:device:deviceType:ver. The
  highest supported version of the device type shall be specified.

  For non-standard devices specified by UPnP vendors, shall begin with "urn:", followed by
  a Vendor Domain Name, followed by ":device:", followed by a device type suffix, colon,
  and an integer version, i.e., "urn:domain-name:device:deviceType:ver". Period characters 
  in the Vendor Domain Name shall be replaced with hyphens in accordance with RFC 2141. 
  The highest supported version of the device type shall be specified.
  """
  def __init__(self, value: str) -> None:
    self._domain = None
    self._urn_type = None
    self._device_type = None
    self._ver = '-1'

    if value is not None:
      values = value.split(':')
      if len(values) == 5:
        _, self._domain, self._urn_type, self._device_type, self._ver = values
      elif len(values) == 4:
        _, self._domain, self._urn_type, self._device_type = values
    self._value = value
    
    # load URN type if possible
    if self._urn_type:
      for _type in urntype:
        if _type.value == self._urn_type:
          self._urn_type = _type
      if type(self._urn_type) == str:
        raise TypeError('Undefined urn-type: "%s"' % self._urn_type)
  
  @property
  def domain(self) -> str:
    """A Vendor Domain Name"""
    return self._domain
    
  @property
  def urn_type(self) -> str:
    """urn specific type"""
    return self._urn_type
    
  @property
  def device_type(self) -> str:
    """device or service type"""
    return self._device_type
    
  @property
  def version(self) -> int:
    """optional version number"""
    return int(self._ver)
    
  def __repr__(self) -> str:
    return self._value
  
  def __str__(self) -> str:
    return self._value

