class Object:
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

  def noop(self, event, event_ctx):
    pass
