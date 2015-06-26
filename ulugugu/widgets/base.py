from ulugugu.events import send_event


class Widget:
  def handle_event(self, event, event_ctx):
    return self.dispatch_event(event, event_ctx)

  def dispatch_event(self, event, event_ctx):
    handler = getattr(self, 'on_%s' % type(event).__name__, None)
    if handler is None:
      raise TypeError("%r misses handler for %r" % (type(self).__name__, type(event).__name__))
    else:
      return handler(event, event_ctx)

  def on_KeyPress(self, press, event_ctx):
    handler = getattr(self, 'on_KeyPress_%s' % press.key, None)
    if handler is None:
      return self.on_KeyPress_default(press, event_ctx)
    else:
      return handler(event_ctx)

  def ignore(self, event, event_ctx):
    pass


class WidgetWrapper(Widget):
  def __init__(self, child):
    self.child = child

  def value(self):
    return self.child.value()

  def width(self):
    return self.child.width()

  def height(self):
    return self.child.height()

  def handle_event(self, event, event_ctx):
    return send_event(self.child, event, event_ctx)

  def draw(self, ctx):
    return self.child.draw(ctx)
