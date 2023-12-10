from logging import exception
import socket

def pprint_info():
  print("[i] You can choose from the following addressees which one you would")
  print("    like to use. (IPv6 not implemented)\n")
  print("I\tFamily", "\t"*5, "Local\n-\t", "-"*6, "\t"*5, "-"*5, sep="")

  index = 1
  default = None
  for family, x, y, z, addr_info in socket.getaddrinfo(socket.gethostname(), 0):
    print("%s\t%s\t%s" % (index, family, addr_info[0]))
    index = index + 1
    if socket.AddressFamily.AF_INET == family and not default:
      default = addr_info[0]

  print("\n[i] Choose your address or let the system take the default one:")
  x = input_address("    - Addressno.: ")
  if x:
    default = x
  print("    - Address   :", default)
  return default

def input_address(prompt):
  try:
    x = int(input(prompt)) - 1
    y = socket.getaddrinfo(socket.gethostname(), 0)

    return y[x][4][0]
  except Exception as e:
    return None



