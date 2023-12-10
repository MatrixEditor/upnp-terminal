__doc__ = """
     UPnP - Universal Plug and Play - Terminal
------------------------------------------------------
[i] For more information about this script use --info
[i] To load everything manually, start with --empty
"""

from .module import (
  UModule
)

from .cc import (
  Context
)

from .perstistencex import (
  DB,
  uuid,
  uobject
)

from .low import (
  notify,
  notifypayload,
  msearch,
  searchpayload,
  soap_body,
  soap_header,
  UDPMulticastClient,
  UDPMulticastListener,
  SSDPHeader,
  SSDPPacket,
  url_fuzz,
  pprint_info
)

from .dd import (
  device,
  service,
  scpd,
  generate_code
)

from ._msearch import (
  MSearchImpl
)

from .discover import (
  DCovImpl
)

from .defaultmodules import (
  IDContext,
  MSearchContext,
  DeviceContext,
  ControlContext
)

from .parsing import (
  UPnPInterpreter,
  ParentContext
)


def __is_located__(x, objectx, predicate):
  if x and predicate:
    for y in objectx:
      if predicate(x, y):
        return True
  return False


# A simple formatting function for printing the methods provided
# through a scpd-file. Don't look at the code just look at the
# printed result.
# Format:
#   [indent] + method_name(param1: type, param2: type): return [value1: type, value3: type]
def format_action(_a, indent='\t\t', param_len=4):
  param = []
  out = []
  action_str = ""
  if not _a.get("argumentList"):
    action_str = '%s|> def %s(): returns None' % (indent, _a.get("name"))
  else:
    for arg in _a.get("argumentList"):
      d = arg.get("direction")
      rsv = arg.get("relatedStateVariable")
      if d == 'in':
        var = ""
        if rsv:
          var = ': ' + rsv
        param.append('%s%s' % (arg.get("name"), var))
      else:  # 'out'
        var = ""
        if rsv:
          var = ': ' + rsv
        out.append('%s%s' % (arg.get("name"), var))

    param = param if len(param) <= param_len else param[:param_len] + ["..."]
    out = out if len(out) <= param_len else param[:param_len] + ["..."]
    if len(out) == 0:
      out = ['None']

    if len(out) > 1:
      action_str = action_str + '%s+ %s(%s):\n%sreturns %s' % (
        indent, _a.get("name"), ', '.join(param), indent * 2, out[0])
    else:
      action_str = action_str + '%s+ %s(%s):\n%sreturns [%s]' % (
        indent, _a.get("name"), ', '.join(param), indent * 2, ', '.join(out))
  return action_str


# A simple formatter for printing the state-variables in
# following syntax:
#   [indent] |> name: value [(default=X)]
def format_var(_v, indent='\t\t'):
  try:
    d = _v["defaultValue"]
  except:
    return '%s|> %s: %s' % (indent, _v["name"], _v["dataType"])

  return '%s| %s: %s (default=%s)' % (indent, _v["name"], _v["dataType"], d)
