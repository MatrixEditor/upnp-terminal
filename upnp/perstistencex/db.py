
from asyncio import exceptions


class uobject:
  def __init__(self, name, value):
    self.name = name
    self.obj = value

  def get(self, index):
    try:
      return self.obj[index]
    except:
      return None

  def is_present(self):
    return self.obj is not None

class DB(object):
  def __init__(self, name=None, full_path=None) -> None:
    if not name and not full_path:
      print("(DB) [ERROR] i-- : a name or path has to be specified")
      raise Exception("[dbERR 404] error in DB.<init>()")

    if full_path:
      self._path = full_path

    if name:
      self._file_name = name

    self._packed = []

  def store(self):
    pass

  def pack(self, o: uobject):
    if not o:
      raise Exception("(upnp.persistence.db) [ERROR] w-- : object to pack is null")
    
    self._packed.append(o)

  def query(self, key: str):
    for o in self._packed:
      if o.name == key:
        return o.obj
    raise Exception("(upnp.persistence.db) [ERROR] -c- : key not found")
    