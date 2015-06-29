from operator import methodcaller
from functools import reduce


def map_(name, iterable):
  return map(methodcaller(name), iterable)


foldl = reduce
