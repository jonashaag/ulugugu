import copy


class Cloneable:
  def clone(self, **overrides):
    klone = copy.copy(self)
    for k, v in overrides.items():
      if not hasattr(self, k):
        raise AttributeError("%r has no attribute %r" % (self, k))
      setattr(klone, k, v)
    return klone

