from ulugugu import sdl, drawings, keys
from ulugugu.events import Event, ACK, MouseEvent, send_event, event_used


class ReceiveChild(Event):
  def __init__(self, child, target_x, target_y, was_dragging, was_focused):
    self.child = child
    self.target_x = target_x
    self.target_y = target_y
    self.was_dragging = was_dragging
    self.was_focused = was_focused

class UnparentChild(Event):
  def __init__(self, former_parent, child, former_x, former_y, was_dragging, was_focused):
    self.former_parent = former_parent
    self.child = child
    self.former_x = former_x
    self.former_y = former_y
    self.was_dragging = was_dragging
    self.was_focused = was_focused


def pt_in_rect(x, y, rx, ry, rw, rh):
  return rx <= x <= rx+rw and ry <= y <= ry+rh


class Object:
  def receive_event(self, event, event_ctx):
    if event in {None, ACK}:
      return event
    else:
      return self.handle_event(event, event_ctx)

  def handle_event(self, event, event_ctx):
    handler = getattr(self, 'on_%s' % type(event).__name__, None)
    if handler is not None:
      return handler(event, event_ctx)

  def on_KeyPress(self, press, event_ctx):
    handler = getattr(self, 'on_KeyPress_%s' % press.key, None)
    if handler is None:
      return self.on_KeyPress_default(press, event_ctx)
    else:
      return handler(event_ctx)

  def on_KeyPress_default(self, _1, _2):
    pass


class SimpleObject(Object):
  def __init__(self, width, height, drawing):
    super().__init__()
    self.width = lambda: width
    self.height = lambda: height
    self.drawing = drawing

  def draw(self, ctx):
    self.drawing.draw(ctx)


class RectangleObject(SimpleObject):
  def __init__(self, width, height, color):
    super().__init__(width, height, drawings.Rectangle(width, height, color))


class TextObject(SimpleObject):
  def __init__(self, text):
    super().__init__(len(text) * 8, 15, drawings.Text(text))


class TextInput(Object):
  allowed_chars = None

  def __init__(self, text):
    self.text = text
    self.height = lambda: 15

  def width(self):
    return len(self.text) * 8

  def draw(self, ctx):
    drawings.Text(self.text).draw(ctx)

  def on_KeyPress_BACKSPACE(self, _):
    self.text = self.text[:-1]
    return ACK

  def on_KeyPress_default(self, press, event_ctx):
    char = keys.to_char(press.key)
    if char:
      if self.allowed_chars is None or char in self.allowed_chars:
        self.text += char
        return ACK


class Value:
  pass

class IntegerValue(Value):
  def __init__(self, value):
    self.value = value

class StringValue(Value):
  def __init__(self, value):
    self.value = value


class IntegerInput(TextInput):
  allowed_chars = '0123456789'

  def __init__(self, default=0):
    super().__init__(str(default))

  @property
  def value(self):
    return IntegerValue(int(self.text))

  def on_KeyPress_KEY_UP(self, _):
    self.text = str(int(self.text) + 1)

  def on_KeyPress_KEY_DOWN(self, _):
    self.text = str(int(self.text) - 1)


class StringInput(TextInput):
  @property
  def value(self):
    return StringValue(self.text)


class Movable:
  def __init__(self, inner, x=0, y=0):
    self.inner = inner
    self.x = x
    self.y = y
  
  def move(self, x, y):
    self.x = x
    self.y = y

  def move_relative(self, xoff, yoff):
    self.x += xoff
    self.y += yoff


class Container(Object):
  unparent_children = True

  def __init__(self, width, height, children=()):
    self.width = lambda: width
    self.height = lambda: height
    self.children = [Movable(child) for child in children]
    self.focused_child = None
    self.dragged_child = None

  def draw(self, ctx):
    for child in self.children:
      with ctx:
        ctx.translate(child.x, child.y)
        with ctx:
          child.inner.draw(ctx)
        if self.focused_child is child:
          border = drawings.Rectangle(
            width=child.inner.width()+4,
            height=child.inner.height()+4,
            color=(0.3, 0.3, 0.8),
            fill='stroke'
          ).move(-2, -2)
          border.draw(ctx)

  def handle_event(self, event, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, event, event_ctx)
      if event_used(response):
        return send_event(self, response, event_ctx)
      else:
        return super().handle_event(event, event_ctx)
    else:
      return super().handle_event(event, event_ctx)

  def send_event_child(self, child, event, event_ctx):
    child_context = event_ctx.clone(
      mouse_x=event_ctx.mouse_x - child.x,
      mouse_y=event_ctx.mouse_y - child.y,
    )
    return send_event(child.inner, event, child_context)

  def on_ReceiveChild(self, event, event_ctx):
    self._add_child_from_drag(event, event.target_x, event.target_y)
    return ACK

  def on_MousePress(self, press, event_ctx):
    children_at_pos = self._get_children_at_pos(event_ctx.mouse_x, event_ctx.mouse_y)
    if children_at_pos:
      self.focused_child = children_at_pos[-1]
      response = self.send_event_child(self.focused_child, press, event_ctx)
      if event_used(response):
        return response
      else:
        self.dragged_child = self.focused_child
    else:
      self._unfocus_child(self.focused_child)

  def on_MouseMove(self, movement, event_ctx):
    if self.dragged_child:
      # Always move first: If we should unparent as  a next step, the child is
      # expected exactly at the border (not a pfew pixels before the border)
      self._raise_child(self.dragged_child)
      self.dragged_child.move_relative(movement.xrel, movement.yrel)

    # Mouse out of bounding box?
    if not pt_in_rect(event_ctx.mouse_x, event_ctx.mouse_y, 0, 0, self.width(), self.height()):
      if self.dragged_child:
        if self.unparent_children:
          return self._unparent_child(event_ctx, self.dragged_child)
        else:
          self._unfocus_child(self.dragged_child)
          return ACK
      else:
        # Mouse out of bounds, no drag => not my departement
        return

    if self.dragged_child:
      for child in reversed(self.children):
        if child is self.dragged_child:
          continue
        if pt_in_rect(event_ctx.mouse_x, event_ctx.mouse_y, child.x, child.y, child.inner.width(), child.inner.height()):
          self._drop_child(event_ctx, self.dragged_child, target=child)

      return ACK

  def on_MouseRelease(self, _1, _2):
    self._stop_dragging()
    
  def on_KeyPress_ESCAPE(self, _):
    if self.focused_child:
      self._unfocus_child(self.focused_child)
      return ACK

  def _unfocus_child(self, child):
    if self.dragged_child is child:
      self._stop_dragging()
    if self.focused_child is child:
      self.focused_child = None

  def _drop_child(self, event_ctx, child, target):
    event = ReceiveChild(
      child        = child.inner,
      target_x     = child.x - target.x,
      target_y     = child.y - target.y,
      was_dragging = child is self.focused_child,
      was_focused  = child is self.dragged_child
    )
    if event_used(self.send_event_child(target, event, event_ctx)):
      self._remove_child(child)
      self.focused_child = target

  def _unparent_child(self, event_ctx, child):
    event = UnparentChild(
      former_parent = self,
      child         = child.inner,
      former_x      = child.x,
      former_y      = child.y,
      was_dragging  = child is self.focused_child,
      was_focused   = child is self.dragged_child
    )
    self._remove_child(child)
    return event

  def _get_children_at_pos(self, x, y):
    return [o for o in self.children if pt_in_rect(x, y, o.x, o.y, o.inner.width(), o.inner.height())]

  def _add_child(self, child, x, y):
    wrapped = Movable(child, x, y)
    self.children.append(wrapped)
    return wrapped

  def _add_child_from_drag(self, event, x, y):
    wrapped_child = self._add_child(event.child, x, y)
    if event.was_focused:
      self.focused_child = wrapped_child
    if event.was_dragging:
      self.dragged_child = wrapped_child

  def _stop_dragging(self):
    self.dragged_child = None

  def _remove_child(self, child):
    self._unfocus_child(child)
    self.children.remove(child)

  def _raise_child(self, child):
    """Push 'child' to top of draw stack"""
    self.children.remove(child)
    self.children.append(child)


class Workspace(Container):
  unparent_children = False

  def on_KeyPress_CHAR_T(self, _):
    self._add_child(StringInput("Some text"), 100, 100)
    return ACK

  def on_KeyPress_CHAR_I(self, _):
    self._add_child(IntegerInput(), 100, 100)
    return ACK

  def on_UnparentChild(self, event, event_ctx):
    former_parent = [c for c in self.children if c.inner == event.former_parent][0]
    self._unfocus_child(former_parent)
    self._add_child_from_drag(
      event,
      former_parent.x + event.former_x,
      former_parent.y + event.former_y
    )

  def draw(self, ctx):
    drawings.Rectangle(
      width=self.width(),
      height=self.height(),
      color=(0, 0, 0),
      fill='stroke'
    ).draw(ctx)
    super().draw(ctx)


class FloatArea(Container):
  def __init__(self, width, height, max_children=None):
    super().__init__(width, height)
    self.max_children = max_children

  def on_ReceiveChild(self, event, event_ctx):
    if self.max_children is None or len(self.children) < self.max_children:
      return super().on_ReceiveChild(event, event_ctx)


class FloatDropArea(FloatArea):
  def draw(self, ctx):
    if self.max_children is None:
      c = 0.2
    else:
      c = len(self.children)/self.max_children * 0.5
    drawings.Rectangle(
      width=self.width(),
      height=self.height(),
      color=(1-c, 1-c, 1-c)
    ).draw(ctx)
    drawings.Rectangle(
      width=self.width(),
      height=self.height(),
      color=(0.9, 0.9, 0.9),
      fill='stroke',
    ).draw(ctx)
    return super().draw(ctx)


class DropArea(Container):
  def draw(self, ctx):
    drawings.Rectangle(
      width=self.width(),
      height=self.height(),
      color=(0.7, 0.9, 0.7),
      fill='stroke',
    ).draw(ctx)
    return super().draw(ctx)

  def _stop_dragging(self):
    super()._stop_dragging()
    if self.children:
      self.children[0].x = 0
      self.children[0].y = 0


class ProgramState:
  def __init__(self, rootobj):
    self.rootobj = rootobj

  def receive_event(self, event, event_ctx):
    self.rootobj.receive_event(event, event_ctx)

  def draw(self, ctx):
    with ctx:
      ctx.set_source_rgb(1,1,1)
      ctx.paint()
    self.rootobj.draw(ctx)


sdl.main(ProgramState(Workspace(700, 500, [DropArea(100, 100)])))
