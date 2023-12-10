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
import urllib3
import xml.etree.ElementTree as xmltree

from .. import all as upnplib
from typing import Iterator

class Callable:
  def __init__(self, action: upnplib.Action, service: upnplib.urn,
               url: str, manager: urllib3.PoolManager) -> None:
    self._manager = manager
    self._action = action
    self._service = service
    self._url = url

  @property
  def boundaction(self) -> upnplib.Action:
    return self._action

  def __call__(self, *args, **kwds) -> upnplib.Envelope:
    for arg_name in kwds:
      self._action.put(arg_name, kwds[arg_name])

    body = upnplib.SoapAction(self._service, action=self._action)
    try:
      envelope = upnplib.Envelope(body)
      body = repr(envelope).encode('utf-8')

      response = self._manager.request('POST', self._url, body=body)
      root = xmltree.fromstring(response.data)

      result = upnplib.Envelope(root=root)
    except Exception as e:
      result = upnplib.Envelope(body=upnplib.Fault(
        type(e).__name__, str(e), 
        response.status, response.reason)
      )
    
    self._cleanup()
    return result

  def _cleanup(self):
    for argument in self._action.in_arguments:
      argument.value = None

  def __repr__(self) -> str:
    return self._action.name

class SubService:
  def __init__(self, device: upnplib.device, ser_desc: upnplib.scpd) -> None:
    self._scpd = ser_desc
    self._device = device
    self._subactions = []
    for action_name in self._scpd.actionList:
      action = self._scpd.actionList[action_name]
      service = self._scpd.service
      head = upnplib.soap_headers(
        action, service.sid.device_type, device.host,
        device.port, service.service_type.version
      )
      target = device.base_url[7:].strip('/').split('/')
      target = 'http://%s' % target[0]

      sub_action = Callable(
        action, service.service_type, 
        '%s/%s' % (target, service.control_url.strip('/')), 
        urllib3.PoolManager(headers=head)
      )
      setattr(self, action_name, sub_action)
      self._subactions.append(sub_action)

  @property
  def name(self) -> str:
    return self._

  def get_scpd(self) -> upnplib.scpd:
    return self._scpd

  def __len__(self) -> int:
    return len(self._subactions)
  
  def __iter__(self) -> Iterator[Callable]:
    return iter(self._subactions)
  
  def __getitem__(self, key):
    return self._subactions[key]

  def find_action(self, action_name: str) -> Callable:
    for action in self._subactions:
      if repr(action) == action_name:
        return action
    return None

  def __contains__(self, item: str) -> bool:
    if type(item) != str: return False
    return self.find_action(item) is not None
  
  def __repr__(self) -> str:
    return str([repr(x) for x in self])
