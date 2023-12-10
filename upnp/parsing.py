import upnp

PROMPT = '\n$:UPnP[%s]> '

class ParentContext(upnp.Context):
  def __init__(self):
    super().__init__("system")
    load0(self)

  def on_action(self, cmd, args= None):
    if cmd == "exit":
      exit(0)
    else:
      print("[i] Unknown command:", cmd)

class UPnPInterpreter:
  def __init__(self, db, modules, context) -> None:
    self.__db = db
    self.__modules = modules
    self.parent = context
    self.context = self.parent

  def accept(self, line):
    if line == "exit":
      exit(0)

    x = line.split(" ")
    sc, ctx = self.change_context(x[0])
    self.context = ctx

    while True:
      try:
        inp = input(PROMPT % self.context.name)
        if not self.context.on_action(inp, self.__db):
          self.context = self.parent
          break
      except Exception as e:
        print("(UPnPInterpreter) [EXCEPTION]:", e)
        break

  def change_context(self, cmd):
    for ctx in self.parent.contexts:
      if ctx.name == cmd:
        return True, ctx
    return False, self.parent

def load0(ctx: upnp.Context):
  ctx.add_ctx(upnp.IDContext())
  ctx.add_ctx(upnp.MSearchContext())
  ctx.add_ctx(upnp.DeviceContext())
  ctx.add_ctx(upnp.ControlContext())
