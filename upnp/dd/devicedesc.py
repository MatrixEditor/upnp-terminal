from xml.etree.ElementTree import Element

NODE_ROOT = 'root'
NODE_SPEC_VERSION = 'specVersion'
NODE_DEVICE = 'device'
NODE_ICON_LIST = 'iconList'
NODE_DEVICE_LIST = 'deviceList'
NODE_SERVICE_LIST = 'serviceList'

# the node-names of a device description below
DEV_DEVICE_TYPE = 'deviceType'
DEV_FRIENDLY_NAME = 'friendlyName'
DEV_MANUFACTURER = 'manufacturer'
DEV_MANUFACTURER_URL = 'manufacturerURL'
DEV_MODEL_DESCRIPTION = 'modelDescription'
DEV_MODEL_NAME = 'modelName'
DEV_MODEL_NUMBER = 'modelNumber'
DEV_MODEL_URL = 'modelURL'
DEV_UDN = 'UDN'
DEV_PRESENTATION_URL = 'presentationURL'

# the node-names of a service description in a
# device description file
SER_SERVICE_TYPE = 'serviceType'
SER_SERVICE_ID = 'serviceID'
SER_CONTROL_URL = 'controlURL'
SER_EVENT_SUB_URL = 'eventSubURL'
SER_SCPD_URL = 'SCPDURL'

NODE_ACTION_LIST = 'actionList'
NODE_STATE_TABLE = 'serviceStateTable'
NODE_STATE_VAR = 'stateVariable'
NODE_DEFAULT_TYPE = 'defaultType'
NODE_DEFAULT_VALUE = 'defaultValue'
NODE_DATA_TYPE = 'dataType'
NODE_ALLOWED_LIST = 'allowedList'
NODE_ALLOWED_RANGE = 'allowedValueRange'
NODE_STEP = 'step'
NODE_MIN = 'minimum'
NODE_MAX = 'max'
NODE_NAME = 'name'

NODE_ARGUMENT_LIST = 'argumentList'
NODE_DIRECTION = 'direction'
NODE_RELATED_VARIABLE = 'relatedStateVariable'


def getname(child: str) -> str:
  """
  Sometimes the xml-parser puts an extra attribute in the
  tag of an Element (also named namespace). This methods removes
  this unnessessary string.
  """
  try:
    return child[child.index("}") + 1:]
  except ValueError:
    return child


class XmlServiceDescription(dict):
  """
  The base class for displaying and saving content of a service description
  """

  def __init__(self, child) -> None:
    super().__init__()

    if child:
      # the .iter() method throws an error on my machine
      for item in child.getchildren():
        self.parse_item(item=item)

  # implementation in sub-classes (device, service, action, scpd)
  def parse_item(self, item):
    pass

  def get(self, key: str):
    try:
      return self[key]
    except:
      return None


class service(XmlServiceDescription):
  def parse_item(self, item: Element):
    name = getname(item.tag)
    self.setdefault(name, item.text)

  def __str__(self) -> str:
    i = self.get(SER_SERVICE_ID)
    s = '[>] %s:\n' % (i if i else 'SERVICE (%s)' % self["serviceId"].split(":")[-1])
    for x in self:
      s += '\t| %s: %s\n' % (x, self[x])
    return s


class StateVar(XmlServiceDescription):
  def __init__(self, child: Element) -> None:
    super().__init__(child=child)

    self.attr = dict()
    if child.attrib:
      self.attr = child.attrib

  def parse_item(self, item: Element):
    name = getname(item.tag)

    if name in [NODE_NAME, NODE_DEFAULT_VALUE, NODE_DATA_TYPE]:
      self.setdefault(name, item.text)
    elif name == NODE_ALLOWED_LIST:
      allowed = [child.text for child in item]
      self.setdefault(name, allowed)
    elif name == NODE_ALLOWED_RANGE:
      range_ = {getname(child.tag): child.text for child in item}
      self.setdefault(name, range_)


class Argument(XmlServiceDescription):
  def __init__(self, child: Element) -> None:
    super().__init__(child=child)

  def parse_item(self, item: Element):
    name = getname(item.tag)

    self.setdefault(name, item.text)


class Action(XmlServiceDescription):
  def __init__(self, child: Element) -> None:
    super().__init__(child=child)

  def parse_item(self, item: Element):
    name = getname(item.tag)

    if name == NODE_NAME:
      self.setdefault(name, item.text)
    elif name == NODE_ARGUMENT_LIST:
      arguments = []
      for argument in item:
        arguments.append(Argument(argument))
      self.setdefault(name, arguments)


class scpd(dict):
  def __init__(self, child: Element) -> None:
    super().__init__()

    if child:
      for item in child:
        if item:
          self.parse_item(item=item)

  def parse_item(self, item: Element):
    name = getname(item.tag)

    if name == NODE_SPEC_VERSION:
      self.setdefault(name, [item[0].text, item[1].text])
    elif name == NODE_ACTION_LIST:
      actions = [Action(a) for a in item]
      self.setdefault(name, actions)
    elif name == NODE_STATE_TABLE:
      statevars = [StateVar(s) for s in item]
      self.setdefault(name, statevars)

  def print_actions(self):
    print("\n[>] scpd - Printing all related actions:")
    for action in self[NODE_ACTION_LIST]:
      print("    | %s" % (action[NODE_NAME]))
      for arg in action[NODE_ARGUMENT_LIST]:
        print(
          " " * 8
          + "| %s: direction=%s (relatedVar=%s)"
          % (
            arg[NODE_NAME],
            arg[NODE_DIRECTION],
            arg.get(NODE_RELATED_VARIABLE),
          )
        )
    print()

  def print_state_table(self):
    print("\n[>] scpd - Printing all related state-variables:")
    for var in self[NODE_STATE_TABLE]:
      print("    | %s: %s" % (var[NODE_NAME], var[NODE_DATA_TYPE]))

      for key in [NODE_DEFAULT_VALUE, NODE_DEFAULT_TYPE]:
        print(" " * 8 + "| %s: %s" % (key, var.get(key)))

      if var.get(NODE_ALLOWED_LIST) != "NONE":
        print(
          " " * 8
          + "| %s: %s"
          % (
            NODE_ALLOWED_LIST,
            "(%s)" % ("; ".join(var.get(NODE_ALLOWED_LIST))),
          )
        )

      if var.get(NODE_ALLOWED_RANGE) != "NONE":
        r = var.get(NODE_ALLOWED_RANGE)
        print(
          " " * 8
          + "| %s: min=%s, max=%s, step=%s"
          % (
            NODE_ALLOWED_RANGE,
            r.get(NODE_MIN),
            r.get(NODE_MAX),
            r.get(NODE_STEP),
          )
        )

  def __str__(self) -> str:
    s = "[>] SCPD:\n"
    for x in self:
      if x == NODE_ACTION_LIST:
        s += '\t|-Action-List:\n'
        for a in self[x]:
          s += self.format_action(a) + '\n'
      elif x == NODE_STATE_TABLE:
        s += '\t|-Service-state-Table:\n'
        for v in self[x]:
          s += self.format_var(v) + '\n'
      else:
        s += '\t| %s: %s\n' % (x, self[x])
    return s

  def format_action(self, _a: Action, indent='\t\t'):
    if _a:
      param = []
      out = []
      if not _a.get(NODE_ARGUMENT_LIST):
        print('%s+ %s():\n%sreturn None\n' % (indent, _a.get(NODE_NAME), indent * 2))
      else:
        for arg in _a.get(NODE_ARGUMENT_LIST):
          d = arg.get(NODE_DIRECTION)
          if d == 'in':
            var = ""
            if arg.get(NODE_RELATED_VARIABLE):
              var = ': ' + arg.get(NODE_RELATED_VARIABLE)
            param.append('%s%s' % (arg.get(NODE_NAME), var))
          else:  # 'out'
            var = ""
            if arg.get(NODE_RELATED_VARIABLE):
              var = ': ' + arg.get(NODE_RELATED_VARIABLE)
            out.append('%s%s' % (arg.get(NODE_NAME), var))

        param = param if len(param) <= 3 else [param[0], param[1], '...']
        out = out if len(out) <= 3 else [out[0], out[1], '...']
        if len(out) == 0:
          out = ['None']

        if len(out) > 1:
          return '%s+ %s(%s):\n%sreturn [%s]\n' % (
            indent, _a.get(NODE_NAME), ', '.join(param), indent * 2, out[0])
        else:
          return '%s+ %s(%s):\n%sreturn [%s]\n' % (
            indent, _a.get(NODE_NAME), ', '.join(param), indent * 2, ', '.join(out))

  # TODO format all stored vars
  def format_var(self, _v, indent='\t\t'):
    try:
      d = _v[NODE_DEFAULT_VALUE]
    except:
      return '%s+ %s: %s' % (indent, _v[NODE_NAME], _v[NODE_DATA_TYPE])
    else:
      return '%s+ %s: %s (default=%s)' % (indent, _v[NODE_NAME], _v[NODE_DATA_TYPE], d)


class device(XmlServiceDescription):
  def parse_item(self, item):
    name = getname(item.tag)

    if name == NODE_SPEC_VERSION:
      self.setdefault(name, [item[0].text, item[1].text])
    elif name in [NODE_ICON_LIST]:
      self.parseList(item=item)
    elif name == NODE_DEVICE_LIST:
      devices = []
      for d in item.getchildren():
        devices.append(device(d))
      self.setdefault(name, devices)
    elif name == NODE_DEVICE:
      for ch in item.getchildren():
        self.parse_item(ch)
    elif name == NODE_SERVICE_LIST:
      services = []
      for ch in item.getchildren():
        s = service(ch)
        services.append(s)
      self.setdefault(name, services)
    else:
      self.setdefault(name, item.text)

  def parseList(self, item: Element):
    # print("[!] Found an icon-list: implementation needed! (device-class)\n")
    pass


def generate_code(desc):
  code = ["// generated by UPnP-Terminal", "", "// at first, the defined variables"]

  variables = desc[NODE_STATE_TABLE]
  types = {}
  for rsv in variables:
    nn = rsv[NODE_NAME]
    nt = rsv[NODE_DATA_TYPE]

    if nn not in types:
      types.setdefault(nn, nt)
    try:
      d = rsv[NODE_DEFAULT_VALUE]
      code.append('define %s %s default %s' % (nt, nn, d))
    except:
      code.append('define %s %s' % (nt, nn))

  code.append("\n// The types are changed to their real types to")
  code.append("// make the understanding easier. For instance, think of the following")
  code.append("// define string A_ARG_TYPE_HelloWorld -> someMethod(string HelloWorld)")

  actions = desc[NODE_ACTION_LIST]
  for action in actions:
    body = []
    arg_list = action.get(NODE_ARGUMENT_LIST)

    if not arg_list:
      code.append("def %s() [void];\n")
      continue

    params = []
    for argument in arg_list:
      rsv__name = argument.get(NODE_RELATED_VARIABLE)
      if argument.get(NODE_DIRECTION) == "in":
        if rsv__name:
          params.append("%s %s" % (types[rsv__name], argument.get(NODE_NAME)))
        else:
          params.append("Any " + argument.get(NODE_NAME))

      else:
        if rsv__name:
          body.append((rsv__name, argument.get(NODE_NAME)))
        else:
          body.append(("Any", argument.get(NODE_NAME)))

    action_str = "def %s(" % action.get(NODE_NAME)
    length = len(action_str)
    param_str = ", ".join(params)
    lines = []

    while len(param_str) > 75:
      try:
        i = param_str.index(",", 75)
        x = param_str[i + 1:]
        param_str = param_str[:i + 1]

        lines.append(" " * length + x)
      except:
        break
    if len(lines) > 0:
      lines[-1] = lines[-1] + "):"
    else:
      param_str = param_str + "):"
    code.append(action_str + param_str)
    for l in lines:
      code.append(l)

    _v = []
    for i, b in enumerate(body):
      n = "var%s" % b[1]
      _v.append(n)
      if b[0] in types:
        code.append("    %s %s = __sub__Get%s(...);" % (types[b[0]], n, b[1]))
      else:
        code.append("    %s %s = __sub__Get%s(...);" % (b[0], n, b[1]))

    code.append("")
    code.append("    return " + ", ".join(_v))
    code.append("")
    code.append("")

  return "\n".join(code)
