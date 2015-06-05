import copy

class Cloneable:
  def clone(self, **overrides):
    klone = copy.copy(self)
    for k, v in overrides.items():
      setattr(klone, k, v)
    return klone

