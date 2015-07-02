import sdl2
from ulugugu import keys, Cloneable


class Event(Cloneable):
  pass


class ACK(Event):
  pass
ACK = ACK()


def send_event(target, event, event_context):
  return target.handle_event(event, event_context)

def event_used(response):
  return response is not None

def try_handlers(handlers):
  def event_handler(self, event, event_ctx):
    for handler in handlers:
      response = handler(self, event, event_ctx)
      if event_used(response):
        return response
  return event_handler


class MouseEvent(Event):
  pass

class MouseMove(MouseEvent):
  def __init__(self, xrel, yrel):
    super().__init__()
    self.xrel = xrel
    self.yrel = yrel

class MousePress(MouseEvent):
  pass

class MouseRelease(MouseEvent):
  pass


class KeyboardEvent:
  def __init__(self, key):
    self.key = key

class KeyPress(KeyboardEvent):
  pass

class KeyRelease(KeyboardEvent):
  pass


def from_sdl_event(sdl_event):
  if sdl_event.type == sdl2.SDL_KEYDOWN:
    return KeyPress(keys.from_keysym(sdl_event.key.keysym.sym))
  elif sdl_event.type == sdl2.SDL_MOUSEBUTTONDOWN:
    return MousePress()
  elif sdl_event.type == sdl2.SDL_MOUSEBUTTONUP:
    return MouseRelease()
  elif sdl_event.type == sdl2.SDL_MOUSEMOTION:
    return MouseMove(sdl_event.motion.xrel, sdl_event.motion.yrel)


class Context(Cloneable):
  def __init__(self, mouse_x, mouse_y):
    self.mouse_x = mouse_x
    self.mouse_y = mouse_y
