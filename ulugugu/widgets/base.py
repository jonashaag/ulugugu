import abc
from ulugugu.events import send_event


class Widget(metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def value(self):
    pass

  @abc.abstractmethod
  def get_drawing(self):
    pass

  def width(self):
    return self.get_drawing().width()

  def height(self):
    return self.get_drawing().height()

  def handle_event(self, event, event_ctx):
    return self.dispatch_event(event, event_ctx)

  def dispatch_event(self, event, event_ctx):
    handler = self.get_event_handler(type(event).__name__)
    return handler(event, event_ctx)

  def get_event_handler(self, event_name):
    return getattr(self, 'on_%s' % event_name, self.on_unhandled_event)

  def on_unhandled_event(self, event, event_ctx):
    raise TypeError("%r misses handler for %r" % (type(self).__name__, type(event).__name__))

  def on_KeyPress(self, press, event_ctx):
    handler = getattr(self, 'on_KeyPress_%s' % press.key, None)
    if handler is None:
      handler = self.get_event_handler('KeyPress_default')
      return handler(press, event_ctx)
    else:
      return handler(event_ctx)

  def ignore(self, event, event_ctx):
    pass


class WidgetWrapper(Widget):
  def __init__(self, child):
    # TODO rename
    self.child = child

  def on_unhandled_event(self, event, event_ctx):
    return send_event(self.child, event, event_ctx)

  def value(self):
    return self.child.value()

  def get_drawing(self):
    return self.child.get_drawing()
