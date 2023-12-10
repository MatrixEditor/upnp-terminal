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

from typing import Iterator
from enum import Enum

from . import (
  SSDP_MULTICAST,
  SSDP_PORT
)

class ssdpmethod(Enum):
  MSEARCH = 'M-SEARCH'
  NOTIFY = 'NOTIFY'
  OK = 'OK'

  @staticmethod
  def valueof(name: str) -> 'ssdpmethod':
    for const in ssdpmethod:
      if const.value == name:
        return const

class man(Enum):
  """It defines the scope (namespace) of the extension."""
  ALIVE = 'alive'
  BYE = 'bye'
  UPDATE = 'update'
  ALL = 'all'
  DISCOVER = 'discover'

  def tostring(self) -> str:
    return 'ssdp:%s' % self.value

class Field:
  def __init__(self, name: str = None, value:str = None,
               line: str = None) -> None:
    self._name = name
    self._value = value
    if line :
      i = line.index(':')
      self._name = line[:i]
      self._value = line[i + 1:].strip()
  
  def __repr__(self) -> str:
    return '%s: %s' % (self._name, self._value)
  
  def __bytes__(self) -> bytes:
    return repr(self).encode('utf-8')

  @property
  def value(self) -> str:
    return self._value.replace('"', '')
  
  @property
  def name(self) -> str:
    return self._name
  
class Message:
  def __init__(self, method: ssdpmethod = ssdpmethod.NOTIFY, path: str = None, 
               http_version: str = 'HTTP/1.1', headers: dict = None, 
               raw_data: str = None) -> None:
    self._method = method
    self._path = path
    self._http_ver = http_version
    self._headers = {}
    if headers:
      for name in headers:
        self._headers[name.lower()] = headers[name]
    if raw_data is not None:
      fields = raw_data.replace('\r', '').splitlines()
      local1, local2, local3 = fields[0].split(' ')
      if local1.startswith('HTTP'):
        self._http_ver = local1
        self._method = ssdpmethod.valueof(local3)
        self._path = int(local2)
      else:
        self._http_ver = local3
        self._method = ssdpmethod.valueof(local1)
        self._path = local2
    
      # now load all header fields
      for line in fields[1:]:
        if not line: continue
        field = Field(line=line)
        self[field.name] = field
    
    for f_name in self:
      self[f_name]._name = f_name
  
  @property
  def method(self) -> ssdpmethod:
    return self._method

  def __getitem__(self, key: str) -> Field:
    key = key.lower()
    for name in self._headers:
      if name.lower() == key:
        return self._headers[name]
  
  def __setitem__(self, key: str, value: str):
    self._headers[key] = value
  
  def __len__(self) -> int:
    return len(self._headers)
  
  def __iter__(self) -> Iterator[str]:
    return iter(self._headers)
  
  def __bytes__(self) -> bytes:
    return repr(self).encode('utf-8')

  def __contains__(self, item):
    item = item.lower()
    for name in self._headers:
      if name.lower() == item:
        return True
    return False

  def __repr__(self) -> str:
    lines = []
    if self._method == ssdpmethod.OK:
      head = '%s %d %s' % (self._http_ver, self._path, self._method.value)
    else:
      head = '%s %s %s' % (self._method.value, self._path, self._http_ver)
    lines.append(head)

    for field_name in self:
      lines.append(repr(self[field_name]))
    
    lines.append('')
    return '\r\n'.join(lines) + '\r\n'

def build_msearch(host: str = SSDP_MULTICAST, port: int = SSDP_PORT, 
                  nspace: man = man.DISCOVER, st: str = 'ssdp:all',
                  mx: int = 2) -> Message:
  return Message(method=ssdpmethod.MSEARCH, path='*', headers={
    'HOST': Field(value='%s:%d' % (host, port)),
    'MAN': Field(value='"%s"' % nspace.tostring()),
    'ST': Field(value=st),
    'MX': Field(value=str(mx))
  })
