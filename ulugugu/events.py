import sdl2
from ulugugu import keys, vec2, Cloneable


class Event(Cloneable):
  def for_child(self, child_position):
    return self.clone()


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
  def __init__(self, relative_movement):
    super().__init__()
    self.relative_movement = relative_movement

class MousePress(MouseEvent):
  pass

class MouseRelease(MouseEvent):
  pass


class KeyboardEvent(Event):
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
    return MouseMove((sdl_event.motion.xrel, sdl_event.motion.yrel))


class Context(Cloneable):
  def __init__(self, mouse_position):
    self.mouse_position = mouse_position

  def for_child(self, child_position):
    return self.clone(mouse_position=vec2.sub(self.mouse_position, child_position))
