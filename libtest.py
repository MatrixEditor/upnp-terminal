# Documentation under preparation
import upnplib.all as upnplib

hosts = upnplib.ssdp_discover('127.0.0.1')

for host_name in hosts:
  host = hosts[host_name]
  print('::%s' % host_name)

  # Get every location url and create a new device
  for location in host.locations:
    print('%s> %s:' % (' '*5, location))
    device = upnplib.new_device(location)

    # the client will close automatically
    with upnplib.Client(device) as devclient:
      services = devclient.services()

      # iterate over the services or directly call a method
      for service_name in services:
        print('%s | %s' % (' '*10, service_name))
        service = services[service_name]
        upnplib.dump_scpd(service.get_scpd(), upnplib.JsonCode, fp='%s.json' % service_name)

      # see fritznox.pseudo for more details on which methods can be used
      response: upnplib.Envelope = devclient.fritzbox.GetMaclist()
      # de-serialize response values 
      mac_list, change_counter = response.unmarshal()
      break

