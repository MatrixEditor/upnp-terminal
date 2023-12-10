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
from ast import arg
from typing import overload
import xml.etree.ElementTree as xmltree

from . import SOAP_SCHEMAS, SOAP_USER_AGENT
from .. import all as upnplib
from ..utils import _xmlrelpath, _xmlfind, _xmlns, _xmlnamespace
from enum import Enum

class XmlnsSoap(Enum):
  SOAP = '%s/soap/envelope/' % SOAP_SCHEMAS
  ADDRESSING = '%s/ws/2004/08/addressing' % SOAP_SCHEMAS
  DISCOVERY = '%s/ws/2005/04/discovery' % SOAP_SCHEMAS
  DEVPROF = '%s/ws/2006/02/devprof' % SOAP_SCHEMAS
  ENNCODING = '%s/soap/encoding/' % SOAP_SCHEMAS

class SoapAction:
  """
  The Simple Object Access Protocol (SOAP) defines the use of XML and HTTP for
  remote procedure calls. UPnP 2.0 uses HTTP to deliver SOAP 1.1 encoded control 
  messages to devices and return results or errors back to control points
  """
  
  @overload
  def __init__(self, serviceType: upnplib.urn = None, 
               action: upnplib.Action = None, 
               root: xmltree.Element = None) -> None: ...

  def __init__(self, serviceType: str = None, action: upnplib.Action = None, 
               root: xmltree.Element = None) -> None:
    self._service_type = serviceType
    self._action = action
    if type(serviceType) == upnplib.urn:
      self._urn = serviceType
      self._service_type = self._urn.device_type
    else:
      self._urn = upnplib.urn('urn:schemas-upnp-org:service:%s' % serviceType) if serviceType else None
    if root is not None:
      name = _xmlrelpath(root)
      self._urn = upnplib.urn(_xmlns(root))
      self._service_type = self._urn.device_type
      args = []
      for argument in root:
        args.append(upnplib.Argument(name=argument.tag, value=argument.text))
      if 'Response' in name:
        self._action = upnplib.Action(name=name.replace('Response', ''), out_arguments=args)
      else: 
        self._action = upnplib.Action(name=name, in_arguments=args)
  
  @property
  def action(self) -> upnplib.Action:
    return self._action
  
  @property
  def servicetype(self) -> str:
    return self._service_type
  
  def __repr__(self) -> str:
    xmlstr = '<u:%s xmlns:u="%s"' % (self.action.name, self._urn)
    args = (self.action.in_arguments 
      if 'Response' not in self.action.name 
      else self.action.out_arguments
    )
    
    if len(args) == 0:
      return '%s/>' % xmlstr
    else:
      xmlstr = '%s>' % xmlstr
    for argument in args: 
      xmlstr = '%s<%s>%s</%s>' % (xmlstr, argument.name, argument.value, argument.name)
    return '%s</u:%s>' % (xmlstr, self.action.name)

class Fault:
  def __init__(self, fault_code: str = None, fault_string: str = None,
               error_code: int = None, error_descr: str = None,
               root: xmltree.Element = None) -> None:
    self._fault_code = _xmlfind(root, 'faultcode') if root else fault_code 
    self._fault_string = _xmlfind(root, 'faultstring') if root else fault_string 
    self._error_code = int(root[2][0][0].text) if root else error_code 
    self._error_descr = root[2][0][1].text if root else error_descr 
  
  @property
  def fault_code(self) -> str:
    return self._fault_code
  
  @property
  def fault_string(self) -> str:
    return self._fault_string
  
  @property
  def error_code(self) -> int:
    return self._error_code
  
  @property
  def error_descr(self) -> str:
    return self._error_descr

  def __repr__(self) -> str:
    xmlstr = '<s:Fault><faultcode>s:%s</faultcode>' % self.fault_code
    xmlstr = '%s<faultstring>%s</faultstring><detail><UPnPError>' % (xmlstr, self.fault_string)
    xmlstr = '%s<errorCode>%s</errorCode><errorDescription>%s</errorDescription>' % (
      xmlstr, self.error_code, self.error_descr
    )
    return '%s</detail></UPnPError></s:Fault>' % xmlstr

class Envelope:
  def __init__(self, body=None, root: xmltree.Element = None) -> None:
    self._body = body
    if root is not None:
      body_element = root[0]
      if 'Fault' in body_element[0].tag:
        self._body = Fault(root=body_element[0])
      else:
        self._body = SoapAction(root=body_element[0])

  def __repr__(self) -> str:
    xmlstr = '<?xml version="1.0" ?>'
    xmlstr += '<s:Envelope xmlns:s="%s" s:encodingStyle="%s">' % (
      XmlnsSoap.SOAP.value, XmlnsSoap.ENNCODING.value
    )
    xmlstr = '%s<s:Body>%s</s:Body>' % (xmlstr, self._body)
    return '%s</s:Envelope>' % (xmlstr)

  @property
  def body(self):
    return self._body

  def unmarshal(self, scpd_obj: upnplib.scpd):
    action = self.body.action
    if self.body is None or action is None: 
      return None

    argv = []
    raction = scpd_obj.actionList[action.name]
    if not raction:
      raise NotImplementedError('Action (%s) not implemented!' % raction.name)

    for argument in action.out_arguments:
      arg = raction.find_out_arg(argument.name)
      if not raction:
        raise NotImplementedError('Argument (%s) not implemented!' % argument.name)

      rst = arg.rst
      argv.append(upnplib.xmltype.unmarshal_str(rst.typename, argument.value))
    return argv

def soap_headers(action: upnplib.Action, service_type: str, host: str, 
                 port: int, service_version: int = -1, 
                 user_agent: str = SOAP_USER_AGENT) -> dict: # dict | None
  # simple non null checks
  if not action or not service_type or not host or not user_agent:
    return None
  if port == -1: return None

  urn_str = 'urn:schemas-upnp-org:service:%s' % (service_type)
  if service_version != -1:
    urn_str = '%s:%d' % (urn_str, service_version)
  return {
    'HOST': '%s:%d' % (host, port),
    'USER-AGENT': user_agent,
    'CONTENT-TYPE': 'text/xml; charset="utf-8"',
    'SOAPACTION': '"%s#%s"' % (urn_str, action.name)
  }
