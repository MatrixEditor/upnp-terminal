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

from typing import Iterator
from . import urn

from ..utils import (
  _xmlfind, 
  _xmlrelpath,
  _xmlnamespace, 
  xmltree
)

class XmlReader:
  def readxml(self, root: xmltree.Element):
    if root is not None:
      for child in root:
        self._readchild(child)

  def _readchild(self, child: xmltree.Element):
    pass

class Icon:
  def __init__(self, mimetype: str = None, width: int = 0, height: int = 0,
               depth: int = 0, url: str = None, root: xmltree.Element = None
              ) -> None:
    nspace = _xmlnamespace(root, 'upnp')
    self._mime = _xmlfind(root, 'upnp:mimetype', namepaces=nspace) if root is not None else mimetype
    self._width = int(_xmlfind(root, 'upnp:width', default='0', namepaces=nspace)) if root is not None else width
    self._height = int(_xmlfind(root, 'upnp:height', default='0', namepaces=nspace)) if root is not None else height
    self._depth = int(_xmlfind(root, 'upnp:depth', default='0', namepaces=nspace)) if root is not None else depth
    self._url = _xmlfind(root, 'upnp:url', namepaces=nspace) if root is not None else url

  @property
  def mimetype(self) -> str:
    return self._mime

  @property
  def width(self) -> int:
    return self._width

  @property
  def height(self) -> int:
    return self._height

  @property
  def depth(self) -> int:
    return self._depth

  @property
  def url(self) -> str:
    return self._url

  def __repr__(self) -> str:
    return '<Icon mime="%s", width=%d, height=%d, depth=%d, uri="%s">' % (
      self.mimetype, self.width, self.height, self.depth, self.url
    )

class Service:
  def __init__(self, s_type: str = None, sid: str = None, scpd_url: str = None,
               control_url: str = None, event_url: str = None, url_base: str = None,
               root: xmltree.Element = None) -> None:
    nspace = _xmlnamespace(root, 'upnp')
    self._service_type = urn(_xmlfind(root, 'upnp:serviceType', namepaces=nspace)) if root is not None else s_type
    self._sid = urn(_xmlfind(root, 'upnp:serviceId', namepaces=nspace) if root is not None else sid)
    self._scpd_url = _xmlfind(root, 'upnp:SCPDURL', namepaces=nspace) if root is not None else scpd_url
    self._control_url = _xmlfind(root, 'upnp:controlURL', namepaces=nspace) if root is not None else control_url
    self._event_url = _xmlfind(root, 'upnp:eventSubURL', namepaces=nspace) if root is not None else event_url
    self._url_base = _xmlfind(root, 'upnp:URLBase', namepaces=nspace) if root is not None else url_base
  
  @property
  def service_type(self) -> urn:
    return self._service_type

  @property
  def sid(self) -> urn:
    return self._sid

  @property
  def scpd_url(self) -> str:
    return self._scpd_url

  @property
  def control_url(self) -> str:
    return self._control_url

  @property
  def event_url(self) -> str:
    return self._event_url

  @property
  def url_base(self) -> str:
    return self._url_base

  def __repr__(self) -> str:
    return '<Service type="%s">' % self.service_type

class ServiceList:
  def __init__(self, root: xmltree.Element = None) -> None:
    self._services = []
    if root is not None:
      for serv in root:
        self.append(Service(root=serv))
  
  def __iter__(self) -> Iterator[Service]:
    return iter(self._services)

  def __getitem__(self, key) -> Service:
    return self._services[key]
  
  def append(self, service: Service):
    self._services.append(service)
  
  def __len__(self) -> int:
    return len(self._services)
  
  def __repr__(self) -> str:
    return repr(self._services)

class device(XmlReader):
  def __init__(self, host: str, port: int, url: str, 
               root: xmltree.Element = None) -> None:
    self._host = host
    self._port = port
    self._url = url
    self._attrib = {}
    self._services: ServiceList = None
    self._embed_devices = []
    self._icons = []
    self.base_url = self.url[:self.url.rindex('/')]
    self.readxml(root)

  @property
  def port(self) -> int:
    return self._port

  @property
  def host(self) -> str:
    return self._host
  
  @property
  def url(self) -> str:
    return self._url
  
  @property
  def iconList(self) -> list:
    return self._icons
  
  @property
  def serviceList(self) -> ServiceList:
    return self._services
  
  @property
  def deviceList(self) -> list:
    return self._embed_devices
  
  @property
  def friendlyname(self) -> str:
    return self['friendlyName']

  @property
  def devicetype(self) -> urn:
    return urn(self['deviceType'])

  def presentationUrl(self) -> str:
    if 'presentationUrl' in self:
      return self['presentationUrl']
    else: return self.url

  def _readchild(self, child: xmltree.Element):
    name = _xmlrelpath(child)

    if name == 'device':
      self.readxml(child)
    elif name == 'iconList':
      self._read_icon_list(child)
    elif name == 'serviceList':
      self._read_services(child)
    elif name == 'deviceList':
      self._read_embedded_devices(child)
    else:
      self[name] = child.text

  def _read_icon_list(self, child: xmltree.Element):
    for icon in child:
      self.iconList.append(Icon(root=icon))
  
  def _read_services(self, child: xmltree.Element):
    self._services = ServiceList(root=child)

  def _read_embedded_devices(self, child: xmltree.Element):
    for node in child:
      self._embed_devices.append(device(self.host, self.port, self.url, root=node))

  def __getitem__(self, key):
    return self._attrib[key]
  
  def __setitem__(self, key, value):
    self._attrib[key]  = value
  
  def __iter__(self) -> Iterator[str]:
    return iter(self._attrib)

def new_device(url: str, proxy: urllib3.ProxyManager = None) -> device:
  manager = proxy if proxy else urllib3.PoolManager(headers={'User-Agent': 'upnplib/1.1'})
  try:
    response = manager.request('GET', url)
    host, port = url[7:].split('/')[0].split(':')
    return device(host, int(port), url, root=xmltree.fromstring(str(response.data, 'utf-8')))
  except Exception as e:
    raise InterruptedError from e
