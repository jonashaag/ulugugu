from ulugugu import sdl, drawings, keys
from ulugugu.events import Event, ACK, KeyPress, send_event, event_used


class ReceiveChild(Event):
  def __init__(self, child, child_xoff, child_yoff):
    self.child = child
    self.child_xoff = child_xoff
    self.child_yoff = child_yoff


class UnparentChild(Event):
  def __init__(self, former_parent, child, child_xoff, child_yoff):
    self.former_parent = former_parent
    self.child = child
    self.child_xoff = child_xoff
    self.child_yoff = child_yoff

class Drag(Event):
  def __init__(self, start_x, start_y, xrel, yrel):
    self.start_x = start_x
    self.start_y = start_y
    self.xrel = xrel
    self.yrel = yrel

class DragStart(Event):
  pass

class DragStop(Event):
  pass


def pt_in_rect(x, y, rx, ry, rw, rh):
  return rx <= x < rx+rw and ry <= y < ry+rh


def rect_in_rect(x1, y1, w1, h1, x2, y2, w2, h2):
  return x2 <= x1 <= x1 + w1 < x2 + w2 and \
         y2 <= y1 <= y1 + h1 < y2 + h2


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


class DragWrapper(Object):
  def __init__(self, wrapped_obj):
    self.wrapped_obj = wrapped_obj
    self.drag_started = False
    self.drag_origin_x = None
    self.drag_origin_y = None

  def on_MousePress(self, event, event_ctx):
    self.drag_origin_x = event_ctx.mouse_x
    self.drag_origin_y = event_ctx.mouse_y
    return send_event(self.wrapped_obj, event, event_ctx)

  def on_MouseRelease(self, event, event_ctx):
    if self.drag_started:
      self.drag_started = False
      send_event(self.wrapped_obj, DragStop(), event_ctx)
    self.drag_origin_x = self.drag_origin_y = None
    return send_event(self.wrapped_obj, event, event_ctx)

  def on_MouseMove(self, event, event_ctx):
    if self.drag_origin_x is None:
      return send_event(self.wrapped_obj, event, event_ctx)
    else:
      if not self.drag_started:
        self.drag_started = True
        send_event(self.wrapped_obj, DragStart(), event_ctx)
      drag_event = Drag(self.drag_origin_x, self.drag_origin_y, event.xrel, event.yrel)
      return send_event(self.wrapped_obj, drag_event, event_ctx)

  def on_KeyPress(self, event, event_ctx):
    return send_event(self.wrapped_obj, event, event_ctx)

  def draw(self, ctx):
    return self.wrapped_obj.draw(ctx)


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

  def on_KeyPress_KEY_DOWN(self, _):
    self.text = str(int(self.text) - 1)


class StringInput(TextInput):
  pass


class Common(Object):
  def send_event_child(self, child, event, event_ctx):
    child_context = event_ctx.clone(
      mouse_x=event_ctx.mouse_x - child.x,
      mouse_y=event_ctx.mouse_y - child.y,
    )
    return send_event(child.inner, event, child_context)

  def get_children_under_cursor(self, event_ctx):
      return self.get_children_at_pos(event_ctx.mouse_x, event_ctx.mouse_y)

  def get_children_at_pos(self, x, y):
    return [o for o in self.children if pt_in_rect(x, y, o.x, o.y, o.inner.width(), o.inner.height())]

  def _maybe_drop_child(self, event_ctx, child, x, y, target):
    if child is target:
      # Can't drop on self
      return
    if rect_in_rect(x, y, child.width(), child.height(),
                    target.x, target.y, target.inner.width(), target.inner.height()):
      return self._drop_child(event_ctx, child, x, y, target)

  def _drop_child(self, event_ctx, child, x, y, target):
    event = ReceiveChild(
      child        = child,
      child_xoff   = event_ctx.mouse_x - x,
      child_yoff   = event_ctx.mouse_y - y,
    )
    return self.send_event_child(target, event, event_ctx)


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


class Container(Common):
  unparent_children = True

  def __init__(self, width, height):
    self.width = lambda: width
    self.height = lambda: height
    self.focused_child = None
    self.children = []

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

  def handle_child_response(self, response, event_ctx):
    if response in {None, ACK}:
      return response
    else:
      if not isinstance(response, UnparentChild):
        raise TypeError("Don't know how to deal with child response %s" % response)
      former_parent = [c for c in self.children if c.inner == response.former_parent][0]
      self._unfocus_child(former_parent)
      self.focused_child = self.add_child(
        response.child,
        event_ctx.mouse_x - response.child_xoff,
        event_ctx.mouse_y - response.child_yoff,
      )
      return ACK

  def on_KeyPress_ESCAPE(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.ESCAPE), event_ctx)
      if event_used(response):
        return response
      else:
        self._unfocus_child(self.focused_child)
        return ACK

  def on_KeyPress_default(self, event, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, event, event_ctx)
      if event_used(response):
        return response

  def on_ReceiveChild(self, event, event_ctx):
    self.focused_child = self.add_child(
      event.child,
      event_ctx.mouse_x - event.child_xoff,
      event_ctx.mouse_y - event.child_yoff
    )
    return ACK

  def on_MousePress(self, press, event_ctx):
    children_at_pos = self.get_children_at_pos(event_ctx.mouse_x, event_ctx.mouse_y)
    if children_at_pos:
      self.focused_child = children_at_pos[-1]
      response = self.send_event_child(self.focused_child, press, event_ctx)
      if event_used(response):
        return response
    else:
      self._unfocus_child(self.focused_child)

  def on_MouseMove(self, event, event_ctx):
    receivers = self.get_children_under_cursor(event_ctx)
    for child in receivers:
        response = self.send_event_child(child, event, event_ctx)
        if event_used(response):
          return self.handle_child_response(response, event_ctx)

  on_DragStart = Object.noop
  on_DragStop = Object.noop

  def on_Drag(self, event, event_ctx):
    if self.focused_child is None:
      return

    response = self.send_event_child(self.focused_child, event, event_ctx)
    if event_used(response):
      return self.handle_child_response(response, event_ctx)

    self._raise_child(self.focused_child)
    self.focused_child.move_relative(event.xrel, event.yrel)

    # Child out of bounding box?
    if not rect_in_rect(self.focused_child.x, self.focused_child.y, self.focused_child.inner.width(), self.focused_child.inner.height(),
                        0, 0, self.width(), self.height()):
      if self.unparent_children:
        return self._unparent_child(event_ctx, self.focused_child)
      else:
        return ACK

    # Child on top of other child => drop?
    for target in reversed(self.children):
      response = self._maybe_drop_child(event_ctx, self.focused_child.inner, self.focused_child.x, self.focused_child.y, target)
      if event_used(response):
        self._remove_child(self.focused_child)
        self.focused_child = target
        return self.handle_child_response(response, event_ctx)

    return ACK

  def on_MouseRelease(self, event, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, event, event_ctx)
      if event_used(response):
        return response

  def _unfocus_child(self, child):
    if self.focused_child is child:
      self.focused_child = None

  def _unparent_child(self, event_ctx, child):
    event = UnparentChild(
      former_parent = self,
      child         = child.inner,
      child_xoff    = event_ctx.mouse_x - child.x,
      child_yoff    = event_ctx.mouse_y - child.y,
    )
    self._remove_child(child)
    return event

  def add_child(self, child, x, y):
    wrapped = Movable(child, x, y)
    self.children.append(wrapped)
    return wrapped

  def _remove_child(self, child):
    self._unfocus_child(child)
    self.children.remove(child)

  def _raise_child(self, child):
    """Push 'child' to top of draw stack"""
    self.children.remove(child)
    self.children.append(child)


class Workspace(Container):
  unparent_children = False

  def on_KeyPress_CHAR_T(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.CHAR_T), event_ctx)
      if event_used(response):
        return response
    self.add_child(StringInput("Some text"), 100, 100)
    return ACK

  def on_KeyPress_CHAR_I(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.CHAR_I), event_ctx)
      if event_used(response):
        return response
    self.add_child(IntegerInput(), 100, 100)
    return ACK

  def draw(self, ctx):
    drawings.Rectangle(
      width=self.width(),
      height=self.height(),
      color=(0, 0, 0),
      fill='stroke'
    ).draw(ctx)
    super().draw(ctx)


class DropArea(Container):
  def draw(self, ctx):
    drawings.Rectangle(
      width=self.width(),
      height=self.height(),
      color=(0.7, 0.9, 0.7),
      fill='stroke',
    ).draw(ctx)
    return super().draw(ctx)

  def on_DragStop(self, event, event_ctx):
    if self.children:
      self.children[0].x = 0
      self.children[0].y = 0


class BesidesWidget(Common):
  def __init__(self, left, right):
    self.width = lambda: left.width() + right.width()
    self.height = lambda: max(left.height(), right.height())
    self.focused_child = None
    self.children = [Movable(left, 0, 0), Movable(right, left.width(), 0)]

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

  def handle_child_response(self, response, event_ctx):
    if response in {None, ACK}:
      return response
    else:
      if not isinstance(response, UnparentChild):
        raise TypeError("Don't know how to deal with child response %s" % response)
      return response.clone(former_parent=self)

  def forward_event_to_focused_child(self, event, event_ctx):
    return self.forward_event_to_child(self.focused_child, event, event_ctx)

  def forward_event_to_child_under_cursor(self, event, event_ctx):
    return self.forward_event_to_child(self.get_child_under_cursor(event_ctx), event, event_ctx)

  on_KeyPress     = forward_event_to_focused_child
  on_Drag         = forward_event_to_focused_child
  on_DragStart    = forward_event_to_focused_child
  on_DragStop     = forward_event_to_focused_child
  on_MouseRelease = forward_event_to_focused_child
  on_MouseMove    = forward_event_to_child_under_cursor

  def on_ReceiveChild(self, event, event_ctx):
    # Child on top of other child => drop?
    for target in reversed(self.children):
      response = self._maybe_drop_child(event_ctx, event.child, event_ctx.mouse_x - event.child_xoff, event_ctx.mouse_y - event.child_yoff, target)
      if event_used(response):
        self.focused_child = target
        return self.handle_child_response(response, event_ctx)

  def on_MousePress(self, event, event_ctx):
    child = self.get_child_under_cursor(event_ctx)
    if child:
      response = self.send_event_child(child, event, event_ctx)
      if event_used(response):
        self.focused_child = child
        return self.handle_child_response(response, event_ctx)
      else:
        return ACK

  def forward_event_to_child(self, child, event, event_ctx):
    if child is not None:
      response = self.send_event_child(child, event, event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)

  def get_child_under_cursor(self, event_ctx):
    children_under_cursor = self.get_children_at_pos(event_ctx.mouse_x, event_ctx.mouse_y)
    if children_under_cursor:
      assert len(children_under_cursor) == 1
      return children_under_cursor[0]


class ProgramState:
  def __init__(self, rootobj):
    self.rootobj = rootobj

  def handle_event(self, event, event_ctx):
    return send_event(self.rootobj, event, event_ctx)

  def draw(self, ctx):
    with ctx:
      ctx.set_source_rgb(1,1,1)
      ctx.paint()
    self.rootobj.draw(ctx)


workspace = Workspace(700, 500)
workspace.add_child(BesidesWidget(DropArea(100, 100), DropArea(100, 100)), 150, 150)
workspace.add_child(DropArea(50, 50), 400, 300)
workspace.add_child(BesidesWidget(IntegerInput(), BesidesWidget(DropArea(50,50), DropArea(100,100))), 10, 10)
sdl.main(ProgramState(DragWrapper(workspace)))
