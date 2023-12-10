from xml.dom import minidom

import requests

import upnp
import argparse

__device_ctx_doc__ = """
[i] The DeviceContext is used to get detailed information about collected 
    devices, services and service-descriptions. The commands are the 
    following ones:
    
    > device [--host HOST] [--name NAME]
        host               the host-address is used to get all devices
                           from that address.
        name               searches for devices wth the given name. If both
                           options are set only 'host' is used
        all                prints all information about stored services
                        
    > service [--name NAME]
        name              only services with the given name will be printed. 
                          
    > scpd [--host HOST_ADDRESS] [--name NAME | --all] [--code PATH] 
        host              prints all service-presentation-descriptions linked 
                          to the host
        name              only services with the given name are printed. It 
                          is recommended to use both options in order to get 
                          less output (it will be huge).
        all               prints and optionally saves all services found to 
                          that host 
        code              creates a pseudocode document with all actions and
                          variables
"""

__msearch_ctx_doc__ = """
[i] The MSearchContext is used to analyze the received packets during the 
    collection process. The following commands are implemented:
    
    > hosts [--save PATH]
        save              writes all collected hosts to the specified path
                          (format=XXX will be added in the future)
"""

__control_ctx_doc__ = """
[i] The ControlContext is used to execute commands on UPnP-Devices. To get a
    feeling of the structure of the declared functions just use the 'code'
    option on 'scpd' in the DeviceContext. This generates a file with pseudocode
    with all global type-definitions and declared methods.
    
    The 'exe' command uses the method-name as an identifier to collect all other 
    details like 'serviceType' or 'controlURL'. If some arguments are required
    the parameter-name is the same as defined in the pseudocode. 
    
    Let's consider the following example: 
            string A_ARG_TYPE_InstanceID
    
    If an argument of the example type is required, the following structure should
    be used:
            --argv InstanceID:someString
  
    The following commands are implemented:
    
    > exe --method METHOD --host HOST [--argv ParamName:Value[,ParamName:Value[,...]]]
        host              the target host
        method            specifies the method name
        argv              if arguments are required, this option has to be used.
                          the structure is described above
    
    > call --host URL --method METHOD --service SERVICE [--argv ParamName:Value[,ParamName:Value[,...]]]
        
"""

DEVICE_PARSER = argparse.ArgumentParser()
DEVICE_PARSER.add_argument("--host", required=False, default=None, type=str)
DEVICE_PARSER.add_argument("--name", required=False, default=None, type=str)
DEVICE_PARSER.add_argument("--all", action="store_true", default=False, required=False)
DEVICE_PARSER.add_argument("--code", required=False, default=None, type=str)

MS_PARSER = argparse.ArgumentParser()
MS_PARSER.add_argument("--save", required=False, default=False, type=str)

CT_PARSER = argparse.ArgumentParser()
CT_PARSER.add_argument("--method", required=False, default=None, type=str)
CT_PARSER.add_argument("--argv", required=False, default=None, type=str)
CT_PARSER.add_argument("--host", required=False, default=None, type=str)
CT_PARSER.add_argument("--service", required=False, default=None, type=str)

class IDContext(upnp.Context):
  def __init__(self):
    super().__init__("upnpId")

  def on_action(self, cmd, args=None):
    argv = cmd.split(" ")
    if argv[0] == "exit":
      return False

    if argv[0] == "new":
      uid = upnp.uuid()
      print("[i] The UUID is used to identify devices in the local network. To know more about")
      print("    the structure of this uuid, refer to the UPnP-Device-Architecture.")
      print("[i] Your Id could be the following one:\n    - uuid :", uid)
    return True

class MSearchContext(upnp.Context):
  def __init__(self):
    super().__init__("msearch")

  def on_action(self, cmd, args=None):
    x = cmd.split(" ")
    argv = MS_PARSER.parse_args(x[1:])

    if not args or x[0] == "exit":
      return False

    if x[0] == "help":
      print(__msearch_ctx_doc__)
      return True

    if x[0] == "hosts":
      if argv.save:
        db_msearch_show_hosts(args, True, argv.save)
      else:
        db_msearch_show_hosts(args)
    elif x[0] == "enum-packets":
      x = -1
      db_msearch_enumerate_packets(args, "--all" in cmd)
    return True

class DeviceContext(upnp.Context):
  def __init__(self):
    super(DeviceContext, self).__init__("devices")

  def on_action(self, cmd, args=None):
    x = cmd.split(" ")
    argv = DEVICE_PARSER.parse_args(x[1:])

    if not args or x[0] == "exit":
      return False

    if x[0] == "help":
      print(__device_ctx_doc__)
      return True

    if x[0] == "device":
      db_device_lookup(args, argv)
    elif x[0] == "service":
      db_service_lookup(args, argv)
    elif x[0] == "scpd":
      db_scpd_lookup(args, argv)
    return True

class ControlContext(upnp.Context):
  def __init__(self):
    super(ControlContext, self).__init__("control")

  def on_action(self, cmd, args=None):
    x = cmd.split(" ")
    argv = CT_PARSER.parse_args(x[1:])

    if not args or x[0] == "exit":
      return False

    if x[0] == "help":
      print(__control_ctx_doc__)
      return True

    if x[0] == "exe":
      db_control_execute(args, argv)
    elif x[0] == "call":
      db_control_call(args, argv)

    return True

def _format_str(x, length):
  if len(x) >= length:
    return x[:length - 3] + "..."
  else:
    return x + " " * (length - len(x))

def _print_service_list(s):
  if s:
    for serv in s:
      x = serv.__str__().replace("\t", "").split("\n")
      print("\t", x[0])
      for line in x[1:]:
        print("\t\t", line)

def db_device_lookup(db, namespace):
  devices = []
  d_types = []
  _device_list = upnp.dd.devicedesc.NODE_DEVICE_LIST
  q = db.query("dcov")

  if not q:
    print("[i] No devices collected. Aborting process.")

  if namespace.host:
    print("[i] Option 'host' specifies all embedded devices related to the HOST. Use")
    print("    the 'name' option to search for a specific device. ")

    h = namespace.host
    for udevice, service, scpd in q:
      url, device__desc = udevice.obj
      if h == url:
        if device__desc.get("deviceType") not in d_types:
          devices.append(udevice.obj)
          d_types.append(device__desc.get("deviceType"))

  elif namespace.name:
    print("[i] The 'name' option searches for device(s) named like the given name.")

    x = namespace.name
    for udevice, service, scpd in q:
      if x == udevice.obj[0]:
        if udevice.get("deviceType") not in d_types:
            devices.append(udevice.obj)
            d_types.append(udevice.obj[1].get("deviceType"))

  if len(devices) > 0:
    print("[i] All devices found with the specified option are listed below:\n")
    for udevice in devices:
      dev = udevice[1]
      print("Name: %s\t- %s" % (dev.get('friendlyName'), dev.get("manufacturer")))
      print("\t|> Model    :", dev.get("modelDescription"))
      print("\t\t| Name :", dev.get("modelName"))
      print("\t|> Type     :", dev.get("deviceType"))
      print("\t|> UDN      :", dev.get("UDN"))
      print("\t|> Services :", dev.get("serviceList") is not None)
      if namespace.all:
        _s: list = dev.get("serviceList")
        _print_service_list(_s)
      print()
  else:
    print("[i] No device found: [DeviceContext]/device_lookup")

def db_service_lookup(db, namespace):
  services = []
  q = db.query("dcov")

  if not q:
    print("[i] No services collected. Aborting process.")

  if namespace.name:
    print("[i] The system is now searching for services running with the name", namespace.name)
    print("    and prints useful information afterwards.")

    for udev, user, uscpd in q:
      if namespace.name in user.obj[1].get("serviceType"):
        services.append(user.obj[1])

    print("[i] Collected ", len(services), "service(s): ")
    x = input("Press 'Enter' to continue...")
    for s in services:
      print("\n", s.__str__())
  else:
    print("[i] Unknown command or no values present: [DeviceContext]/service_lookup")

def db_scpd_lookup(db, namespace):
  services = []
  q = db.query("dcov")

  if not q:
    print("[i] No service-descriptions collected. Aborting process.")

  if namespace.host:
    if not namespace.name:
      print("[i] Warning: The 'host' option should be always used in connection with the ")
      print("    'name' option. Otherwise, too much output will be generated.")

    for udev, user, uscpd in q:
      if namespace.host == udev.obj[0]:
        services.append((user.obj[1], uscpd.obj))

  if namespace.name:
    print("[i] Option 'name' enabled: service-description with the following name ")
    print("    will be printed: '", namespace.name, "'", sep="")
    if len(services) == 0:
      for udev, user, uscpd in q:
        if namespace.name in user.obj[1].get("serviceType"):
          services.append((user.obj[1], uscpd.obj))
    else:
      new_services = []
      for x, y in services:
        if namespace.name in x.get("serviceType"):
          new_services.append((x, y))
      services = new_services

  if len(services) > 0:
    for service, desc in services:
      print("\nService:", service.get("serviceId"), "[", desc[0], "]")
      al = desc[1].get("actionList")
      vl = desc[1].get("serviceStateTable")

      if al:
        print("\t| Actions:")
        for action in al:
          print(upnp.format_action(action, indent="\t\t", param_len=3))
      if vl:
        print("\t| RelatedStateVariables:")
        for rsv in vl:
          print(upnp.format_var(rsv, indent="\t\t"))

      if namespace.code:
        path = namespace.code
        with open(path + service.get("serviceId").split(":")[-1] + ".txt", "w") as _f:
          _f.write(upnp.generate_code(desc[1]))
  else:
    print("[i] Unknown command or no values present: [DeviceContext]/scpd_lookup")

def db_msearch_show_hosts(db, save=False, to=None):
  print("[i] Below all devices that support UPnP in the local network are listed.")
  if not save:
    print("    It is also possible to save the output to a file (currently only txt)")
    print("    simply by adding --save PATH to the command.")

  q = db.query("msearch")
  if not q:
    print("[i] No packets collected -> no devices found")

  packets = q['packets']
  if not packets or len(packets) == 0:
    print("[i] No packets collected -> no devices found")
    return

  print("\nI\tAddress\t\t\t%sLocation" % _format_str("Type", 75))
  print("--\t", "-" * 7, "\t\t\t", "-" * 15, _format_str(" ", 60),"-" * 8, sep="")
  table = []
  for index, p in enumerate(packets):
    loc = p.get('LOCATION')
    if loc not in table:
      s = _format_str(p.get('SERVER'), 75)
      print("%s\t%s\t%s%s" % (index, p.host, s, loc))
      table.append(loc)

def db_msearch_enumerate_packets(db, a_p=True, number=-1):
  print("[i] Implementation needed.")

def db_control_execute(db, namespace):
  q = db.query("dcov")
  if not q:
    print("[i] No values in database. Aborting process.")
    return

  if not namespace.method:
    print("[i] Please specify the host or method")
    return

  target = None
  service = None
  for ud, us, usc in q:
    if service or target:
      break

    if namespace.host and not namespace.host == ud.obj[0]:
      continue

    l = usc.obj[1].get("actionList")
    if not l:
      continue

    for m in l:
      if m.get("name") == namespace.method:
        service = us.obj[1].get("serviceType")
        x = usc.obj[0][7:].split("/")[0]
        y = us.obj[1].get("controlURL")
        z = "" if "/" in y[:2] else "/"
        target = "http://" + x + z + y
        break

  if not service or not target:
    print("[i] No methods found related to the given name.")
    return

  if namespace.argv:
    tmp = [x.split(":") for x in namespace.argv.split(",")]
    args = tmp
  else:
    args = []

  soap__body = upnp.soap_body(service, namespace.method, args)
  soap__header = upnp.soap_header(service, namespace.method)

  print(target)
  print(str(soap__body))
  resp = requests.post(url=target, headers=soap__header, data=bytes(soap__body, 'utf-8'))
  try:
    soap__response = minidom.parseString(resp.text)
  except Exception as e:
    print("[i] Error while reading occurred:", e)
    return

  print("[i] The system got a response! Usually there will be an error")
  print("    displayed when looking at the text, due to invalid formatting")
  print("    or invalid arguments.\n")
  x = soap__response.toprettyxml().split("\n")
  for line in x:
    if not line or len(line) == 0 or line == "\t" or line == "\t\t":
      continue
    print(line)

def db_control_call(db, namespace):
  if namespace.argv:
    tmp = [x.split(":") for x in namespace.argv.split(",")]
    args = tmp
  else:
    args = []

  soap__body = upnp.soap_body(namespace.service, namespace.method, args)
  soap__header = upnp.soap_header(namespace.service, namespace.method)

  resp = requests.post(url=namespace.host, headers=soap__header, data=bytes(soap__body, 'utf-8'))
  try:
    soap__response = minidom.parseString(resp.text)
  except Exception as e:
    print("[i] Error while reading occurred:", e)
    return

  print("[i] The system got a response! Usually there will be an error")
  print("    displayed when looking at the text, due to invalid formatting")
  print("    or invalid arguments.\n")
  x = soap__response.toprettyxml().split("\n")
  for line in x:
    if not line or len(line) == 0 or line == "\t" or line == "\t\t":
      continue
    print(line)