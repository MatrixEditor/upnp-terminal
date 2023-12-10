class Context:
  def __init__(self, n, other=None):
    if other is None:
      other = []

    self.name = n
    self.contexts = other

  def on_action(self, cmd, args=None):
    return False

  def add_ctx(self, c):
    self.contexts.append(c)