import operator
from functools import partial


def scale(vec, factor):
  x, y = vec
  return (x * factor, y * factor)


def add(v1, v2):
  x1, y1 = v1
  x2, y2 = v2
  return (x1 + x2, y1 + y2)


def sub(v1, v2):
  return add(v1, neg(v2))


def neg(vec):
  x, y = vec
  return (-x, -y)


def _compare(cmp_f, *vecs):
  for v1, v2 in zip(vecs, vecs[1:]):
    for component1, component2 in zip(v1, v2):
      if not cmp_f(component1, component2):
        return False
  return True


lt = partial(_compare, operator.lt)
le = partial(_compare, operator.le)
gt = partial(_compare, operator.gt)
ge = partial(_compare, operator.ge)
