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
The UPnP description for a service defines actions and their arguments, and state
variables and their data type, range, and event characteristics.
"""
import urllib3

from enum import Enum

from ..utils import  (
  xmltree,
  _xmlfind,
  _xmlnamespace,
  _xmlfind_attr
)

from . import typeof, urn, Service

class direction(Enum):
  IN = 'in'
  OUT = 'out'

  @staticmethod
  def parse_direction(root: xmltree.Element) -> 'direction':
    if root.text == 'in': return direction.IN
    else: return direction.OUT

class StateVariable:
  def __init__(self, name: str = None, data_type: type = None, default=None,
               allowedValues: list = None, eventing: bool = False, 
               allowedValueRange: range = None, multicast: bool = False, 
               root: xmltree.Element = None, nspace: dict = None) -> None:
    self._name = _xmlfind(root, 'upnp:name', namepaces=nspace) if root is not None else name
    self._data_type_name = _xmlfind(root, 'upnp:dataType', namepaces=nspace) if root is not None else data_type
    self._default = _xmlfind(root, 'upnp:defaultValue', namepaces=nspace) if root is not None else default
    self._eventing = root.get('sendEvents') if root is not None else eventing
    self._multicast = root.get('multicast', default=False) if root is not None else multicast
    self._allowed_range = allowedValueRange
    self._allowed_values = allowedValues if allowedValues else []
    self._complex_type = None
    if root is not None:
      self._allowed_range = _xmlfind(
        root, 
        'upnp:allowedValueRange', 
        default=None, 
        extractor=self._load_range,
        namepaces=nspace
      )
      self._allowed_values = _xmlfind(
        root, 
        'upnp:allowedValueList',
        default=[],
        extractor=self._load_allowed_values,
        namepaces=nspace
      )
      complex_type = _xmlfind_attr(root, 'upnp:dataType', 'type', namepaces=nspace)
      if complex_type is not None:
        if len(complex_type.split(':')) > 2:
          self._complex_type = urn(complex_type)

    self._data_type = typeof(self._data_type_name)

  @property
  def name(self) -> str:
    """Name of state variable."""
    return self._name

  @property
  def typename(self) -> str:
    return self._data_type_name

  @property
  def data_type(self) -> type:
    """Same as data types defined by XML Schema."""
    return self._data_type

  @property
  def default(self):
    return self._default

  @property
  def eventing(self) -> bool:
    """
    Defines whether event messages will be generated when the value of this
    state variable changes. 
    
    Default value is "yes". Non-evented state variables shall set this attribute
    to "no".
    """
    return self._eventing

  def is_multicast(self) -> bool:
    """
    Defines whether event messages will be delivered using multicast eventing.

    Default value is "no". If the multicast is set to "yes", then all events 
    sent for this state variable shall be unicast AND multicast.
    """
    return self._multicast

  def has_complex_type(self) -> bool:
    return self._complex_type is not None
  
  @property
  def complex_type(self) -> urn:
    return self._complex_type

  @property
  def allowed_range(self) -> range:
    return self._allowed_range

  @property
  def allowed_values(self) -> list:
    return self._allowed_values

  def _load_range(self, root: xmltree.Element) -> range:
    nspace = _xmlnamespace(root, 'upnp')
    start = int(_xmlfind(root, 'upnp:minimum', default='0', namepaces=nspace))
    stop = int(_xmlfind(root, 'upnp:maximum', default='0', namepaces=nspace))
    step = int(_xmlfind(root, 'upnp:step', default='1', namepaces=nspace))
    return range(start, stop, step)
  
  def _load_allowed_values(self, root: xmltree.Element) -> list:
    values = []
    for value in root.findall('allowedValue'):
      values.append(value.text)
    return values
  
  def __repr__(self) -> str:
    return '<StateVariable name="%s", %s>' % (self.name, self.data_type)

  def __call__(self, *args, **kwds):
    return self._data_type(*args, **kwds)

class Argument:
  def __init__(self, name: str = None, arg_direction: direction = direction.IN,
               rst: StateVariable = None, root: xmltree.Element = None,
               nspace: dict = None, value=None) -> None:
    self._name = _xmlfind(root, 'upnp:name', namepaces=nspace) if root is not None else name
    self._arg_direction = (
      _xmlfind(root, 'upnp:direction', namepaces=nspace, extractor=direction.parse_direction) 
      if root is not None 
      else arg_direction
    )
    self._related_state_variable = (
      _xmlfind(root, 'upnp:relatedStateVariable', namepaces=nspace) 
      if root is not None 
      else rst
    )
    self.value = value
  
  @property
  def name(self) -> str:
    return self._name

  @property
  def arg_direction(self) -> direction:
    return self._arg_direction

  def rst_name(self) -> str:
    """Shall be the name of a state variable. 
    
    Case Sensitive. Defines the type of the argument;"""
    return self.rst.name

  @property
  def rst(self) -> StateVariable:
    return self._related_state_variable

  def __repr__(self) -> str:
    return '<Argument name="", %s, var="%s">' % (
      self.name, self.arg_direction.value, self.rst_name()
    )

class Action:
  def __init__(self, name: str = None, in_arguments: list = None,
               out_arguments: list = None, root: xmltree.Element = None,
               nspace: dict = None) -> None:
    self._name = _xmlfind(root, 'upnp:name', namepaces=nspace) if root is not None else name
    self._in_arguments = in_arguments if in_arguments else []
    self._out_arguments = out_arguments if out_arguments else []
    if root is not None:
      for arg_node in root.find('upnp:argumentList', nspace):
        arg = Argument(root=arg_node, nspace=nspace)
        if arg.arg_direction == direction.IN:
          self._in_arguments.append(arg)
        else: self._out_arguments.append(arg)

  @property
  def name(self) -> str:
    return self._name

  @property
  def in_arguments(self) -> list: 
    return self._in_arguments

  @property
  def out_arguments(self) -> list:
    return self._out_arguments

  def find_out_arg(self, name: str) -> Argument:
    for arg in self.out_arguments:
      if arg.name == name: return arg

  def put(self, arg_name: str, value):
    for argument in self.in_arguments:
      if argument.name == arg_name:
        argument.value = value
        break

  def __repr__(self) -> str:
    return '<Action name="%s", inargs=%d, outargs=%d>' % (
      self.name, len(self.in_arguments), len(self.out_arguments)
    )

class scpd:
  def __init__(self, service: Service, root: xmltree.Element = None) -> None:
    self._state_vars = {}
    self._actions = {}
    self._service = service
    if root is not None:
      namespace = _xmlnamespace(root, 'upnp')

      for var in root.find('upnp:serviceStateTable', namespace):
        s0 = StateVariable(root=var, nspace=namespace)
        self.setval('vars', s0)

      for action in root.find('upnp:actionList', namespace):
        a0 = Action(root=action, nspace=namespace)
        self._add_action(a0)

  def _add_action(self, a0: Action):
    for xlist in [a0.in_arguments, a0.out_arguments]:
      for in_arg in xlist:
        if in_arg.rst in self._state_vars:
          in_arg._related_state_variable = self._state_vars[in_arg.rst]
        else:
          raise ValueError('ArgumentType not found: %s' % (in_arg.rst))
    self.setval('action', a0)
      
  def setval(self, context: str, value):
    if context == 'action':
      self._actions[value.name] = value
    elif context == 'vars':
      self._state_vars[value.name] = value

  @property
  def actionList(self) -> dict:
    return self._actions

  @property
  def svars(self) -> dict:
    return self._state_vars

  @property
  def service(self) -> Service:
    return self._service

  def __repr__(self) -> str:
    return '<scpd actions=%d, variables=%d>' % (
      len(self.actionList), len(self.svars)
    )
