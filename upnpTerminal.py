import upnp

import argparse
import sys

main_parser = argparse.ArgumentParser("upnpTerminal")
main_parser.add_argument("--empty", action="store_true", required=False, default=False)
main_parser.add_argument("--hide", action="store_true", required=False, default=False)

def init_modules():
  m0 = upnp.MSearchImpl(1)
  m1 = upnp.DCovImpl(2)
  return [m0, m1]


def start():
  a = upnp.pprint_info()
  x = main_parser.parse_args()

  udp_client = upnp.UDPMulticastClient(address=a)
  user_db = upnp.DB() if x.empty else upnp.DB("temp.local")
  m = init_modules()

  if not x.empty:
    print("[i] Loading database...")
    for umodule in m:
      if not x.empty:
        umodule.execute(udp_client, db=user_db)

  interpreter = upnp.UPnPInterpreter(user_db, m, upnp.ParentContext())
  while True:
    try:
      interpreter.accept(input('\n$:UPnP[system]> '))
    except Exception as e:
      print("(upnp.terminal) [EXCEPTION] -c- :", e)


if __name__ == '__main__':
  print(upnp.__doc__)
  start()
