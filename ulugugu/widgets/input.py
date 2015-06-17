from ulugugu import drawings, keys
from ulugugu.widgets import *
from ulugugu.events import ACK


class TextInput(Object):
  allowed_chars = None

  def __init__(self, text):
    self.text = text
    self.height = lambda: 15

  def width(self):
    return len(self.text) * 8

  def draw(self, ctx):
    drawings.Text(self.text).draw(ctx)

  on_MousePress = Object.noop
  on_MouseRelease = Object.noop
  on_MouseMove = Object.noop
  on_Drag = Object.noop
  on_DragStart = Object.noop
  on_DragStop = Object.noop

  def on_KeyPress_BACKSPACE(self, _):
    self.text = self.text[:-1]
    return ACK

  def on_KeyPress_default(self, press, event_ctx):
    char = keys.to_char(press.key)
    if char:
      if self.allowed_chars is None or char in self.allowed_chars:
        self.text += char
        return ACK


class IntegerInput(TextInput):
  allowed_chars = '0123456789'

  def __init__(self, default=0):
    super().__init__(str(default))

  def on_KeyPress_KEY_UP(self, _):
    self.text = str(int(self.text) + 1)
    return ACK

  def on_KeyPress_KEY_DOWN(self, _):
    self.text = str(int(self.text) - 1)
    return ACK


class StringInput(TextInput):
  pass
