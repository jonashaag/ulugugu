class Value:
  pass

class Integer(Value):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return '<Integer %d>' % self.value


class String(Value):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return '<String %r>' % self.value


class Application(Value):
  def __init__(self, operation, op1, op2):
    self.operation = operation
    self.op1 = op1
    self.op2 = op2

  def __str__(self):
    return '<Application %s(%s, %s)>' % (self.operation, self.op1, self.op2)
