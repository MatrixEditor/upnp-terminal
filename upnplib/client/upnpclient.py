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
import xml.etree.ElementTree as xmltree

from .. import all as upnplib
from ..utils import fuzz_request
from . import SubService

class Client:
  def __init__(self, device: upnplib.device) -> None:
    self._device = device
    self._services = {}
    self._load_device(device)

  def services(self) -> dict:
    return self._services

  def _load_device(self, device: upnplib.device):
    # preventing more than one executions of this method
    if len(self._services) != 0: return

    for service in device.serviceList:
      url_base = '%s/%s' % (device.base_url.strip('/'), service.scpd_url.strip('/'))
      response = fuzz_request(url_base)
      if response is not None and response.status == 200:
        if response.data:
          s_desc = upnplib.scpd(service, xmltree.fromstring(response.data))
          serv = upnplib.SubService(device, s_desc)

          setattr(self, service.sid.device_type, serv)
          self._services[service.sid.device_type] = serv
    for dev in device.deviceList:
      self._load_device(dev)
    
  def find_service(self, name: str) -> SubService:
    return self[name]

  def __enter__(self) -> 'Client':
    return self

  def __contains__(self, item: str) -> bool:
    return item in self._services

  def __exit__(self, e_type, e, traceback):
    pass

  def __getitem__(self, key) -> SubService:
    if key in self:
      return self._services[key]

  
  


