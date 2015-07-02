from ulugugu import drawings, keys, values
from ulugugu.widgets import Widget
from ulugugu.events import ACK


class InputWidget(Widget):
  on_ReceiveChild = Widget.ignore
  on_Drag = Widget.ignore
  on_DragStart = Widget.ignore
  on_DragStop = Widget.ignore


class TextInput(InputWidget):
  allowed_chars = None

  def __init__(self, text):
    self.text = text

  def get_drawing(self):
    return drawings.Text(self.text)

  on_MousePress = Widget.ignore
  on_MouseRelease = Widget.ignore
  on_MouseMove = Widget.ignore

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

  def value(self):
    return values.Integer(int(self.text))


class StringInput(TextInput):
  def value(self):
    return values.String(self.text)
