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

import socket
import struct

from typing import Iterator, overload
from . import (
  SSDP_MULTICAST,
  SSDP_PORT,

  Message,
  build_msearch
)

class ssdpagent:
  def __init__(self, ttl: int = 2, address: str = None, iface: str = None) -> None:
    self._error__handlers = []
    self._iter_amount = -1

    self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self._sock.settimeout(5)

    ttl = struct.pack('b', ttl)
    self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    self._address = (SSDP_MULTICAST, SSDP_PORT)
    if address is not None:
      self._sock.bind((address, 0))
    if iface is not None:
      self._sock.setsockopt(socket.SOL_SOCKET, getattr(socket, "SO_BINDTODEVICE", 25), iface)
  
  def add_error_handler(self, handler):
    if handler: self._error__handlers.append(handler)

  def close(self):
    self._sock.close()

  def write_object(self, obj) -> int:
    return self._sock.sendto(bytes(obj), self._address)

  def prepare_iter(self, amount: int):
    self._iter_amount = amount

  def interrupt(self):
    self._iter_amount = 0

  def _notify_handlers(self, error):
    for handler in self._error__handlers:
      handler(error)
    
  def __iter__(self):
    try:
      counter = 0
      while True:
        if self._iter_amount > 0 and self._iter_amount <= counter:
          break
        counter += 1
        data, address = self._sock.recvfrom(1024)
        yield Message(raw_data=str(data, 'utf-8')), address[0], address[1]
    except socket.timeout as tout:
      self._notify_handlers(tout)
  
  def __enter__(self) -> 'ssdpagent':
    return self
  
  def __exit__(self, exc_type, exc_value, traceback):
    if exc_type is not None:
      self._notify_handlers(exc_value)
    self.close()
  
class ssdphost:
  def __init__(self, host: str) -> None:
    self._host = host
    self._devices= []
  
  @property
  def host(self) -> str:
    return self._host

  @property
  def locations(self) -> list:
    return self._devices
  
  def __iadd__(self, other):
    if other.value not in self._devices:
      self._devices.append(other.value)
    return self
  
  def __repr__(self) -> str:
    return '<Host target="%s", devices=%d>' % (self.host, len(self.locations))

class ssdpresult:
  def __init__(self) -> None:
    self._hosts = {} # type: list[ssdphost]

  def __iter__(self) -> Iterator[str]:
    return iter(self._hosts)

  def __setitem__(self, key: str, host: ssdphost):
    self._hosts[key] = host
  
  def __getitem__(self, key: str) -> ssdphost:
    if key in self:
      return self._hosts[key]
  
  def __contains__(self, item) -> bool:
    return item in self._hosts
  
  def __len__(self) -> int:
    return len(self._hosts)
  
  @overload
  def __iadd__(self, other: ssdphost) -> 'ssdpresult': ...
  def __iadd__(self, other: tuple) -> 'ssdpresult':
    if type(other) == tuple:
      host, device = other
      if host in self:
        self[host] += device
    else:
      self[other.host] = other
    return self

  def __repr__(self) -> str:
    return repr(self._hosts)

def ssdp_discover(address: str) -> ssdpresult:
  result = ssdpresult()
  with ssdpagent(address=address) as client:
    client.write_object(build_msearch())
    for packet, address, port in client:
      if 'LOCATION' in packet:
        if address in result:
          result +=  (address, packet['LOCATION'])
        else:
          host = ssdphost(address)
          host += packet['LOCATION']
          result += host
      else:
        print(address)
  return result
