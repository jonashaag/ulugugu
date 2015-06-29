import cairocffi as cairo
import ctypes
import sdl2
import sdl2.ext

from ulugugu import events


def main(state):
  sdl2.ext.init()
  window = sdl2.ext.Window("ulugugu", (800,600))
  window.show()
  loop(window, state)
  sdl2.ext.quit()


def loop(window, state):
  sdl_event = sdl2.SDL_Event()
  should_redraw = True

  while True:
    while sdl2.SDL_PollEvent(ctypes.byref(sdl_event)):
      if sdl_event.type == sdl2.SDL_QUIT:
        return

      event = events.from_sdl_event(sdl_event)
      if event:
        event_context = get_event_context()
        events.send_event(state, event, event_context)
        should_redraw = True

    if should_redraw:
      draw_cairo(window, state.draw)
      window.refresh()
      should_redraw = False

    sdl2.SDL_Delay(10)


def draw_cairo(window, drawer):
  sdl_surface = window.get_surface()

  if sdl2.SDL_MUSTLOCK(sdl_surface):
    sdl2.SDL_LockSurface(sdl_surface)

  stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_RGB24, sdl_surface.w)
  buffer_size = stride * sdl_surface.h
  cairo_surface = cairo.ImageSurface(
    cairo.FORMAT_RGB24,
    sdl_surface.w,
    sdl_surface.h,
    cairo.ffi.buffer(cairo.ffi.cast('char*', sdl_surface.pixels), buffer_size)
  )
  cairo_ctx = cairo.Context(cairo_surface)
  drawer(cairo_ctx)

  if sdl2.SDL_MUSTLOCK(sdl_surface):
    sdl2.SDL_UnlockSurface(sdl_surface)


def get_mouse_state():
  x = ctypes.c_int()
  y = ctypes.c_int()
  sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
  return (x.value, y.value)


def get_event_context():
  return events.Context(*get_mouse_state())
