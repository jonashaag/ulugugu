from ulugugu import drawings, keys
from ulugugu.events import ACK, KeyPress, send_event, event_used
from ulugugu.widgets import *
from ulugugu.utils import rect_in_rect


class Workspace(Container):
  def __init__(self, width, height):
    self.width = lambda: width
    self.height = lambda: height
    self.focused_child = None
    self.children = []

  def draw(self, ctx):
    super().draw(ctx)
    drawings.Rectangle(
      width=self.width(),
      height=self.height(),
      color=(0.7, 0.7, 0.7),
      fill='stroke'
    ).draw(ctx)

  def handle_child_response(self, response, event_ctx):
    if response in {None, ACK}:
      return response
    else:
      if not isinstance(response, UnparentChild):
        raise TypeError("Don't know how to deal with child response %s" % response)
      former_parent = [c for c in self.children if c.inner == response.former_parent][0]
      self.focused_child = self.add_child(
        response.child,
        event_ctx.mouse_x - response.child_xoff,
        event_ctx.mouse_y - response.child_yoff,
      )
      return ACK

  on_KeyPress_default = Container.forward_event_to_focused_child
  on_MouseMove = Container.forward_event_to_child_under_cursor
  on_MouseRelease = Container.forward_event_to_focused_child
  on_DragStart = Container.forward_event_to_focused_child
  on_DragStop  = Container.forward_event_to_focused_child

  def on_KeyPress_CHAR_T(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.CHAR_T), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
    self.add_child(StringInput("Some text"), 100, 100)
    return ACK

  def on_KeyPress_CHAR_I(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.CHAR_I), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
    self.add_child(IntegerInput(), 100, 100)
    return ACK

  def on_KeyPress_ESCAPE(self, event_ctx):
    if self.focused_child:
      response = self.send_event_child(self.focused_child, KeyPress(keys.ESCAPE), event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
      else:
        self.focused_child = None
        return ACK

  def on_ReceiveChild(self, event, event_ctx):
    self.focused_child = self.add_child(
      event.child,
      event_ctx.mouse_x - event.child_xoff,
      event_ctx.mouse_y - event.child_yoff
    )
    return ACK

  def on_Drag(self, event, event_ctx):
    if self.focused_child is None:
      return

    response = self.send_event_child(self.focused_child, event, event_ctx)
    if event_used(response):
      return self.handle_child_response(response, event_ctx)

    self.raise_child(self.focused_child)
    self.focused_child.move_relative(event.xrel, event.yrel)

    # Child out of bounding box?
    if not rect_in_rect(self.focused_child.x, self.focused_child.y, self.focused_child.inner.width(), self.focused_child.inner.height(),
                        0, 0, self.width(), self.height()):
      return self.unparent_child(event_ctx, self.focused_child)

    target, child_response = self.maybe_drop_child(self.focused_child, event_ctx)
    if event_used(child_response):
      self.children.remove(self.focused_child)
      self.focused_child = target
      return self.handle_child_response(child_response, event_ctx)

    return ACK

  def unparent_child(self, event_ctx, child):
    event = UnparentChild(
      former_parent = self,
      child         = child.inner,
      child_xoff    = event_ctx.mouse_x - child.x,
      child_yoff    = event_ctx.mouse_y - child.y,
    )
    self.children.remove(self.focused_child)
    self.focused_child = None
    return event

  def add_child(self, child, x, y):
    wrapped = PositionedChild(child, x, y)
    self.children.append(wrapped)
    return wrapped

  def raise_child(self, child):
    """Push 'child' to top of draw stack"""
    self.children.remove(child)
    self.children.append(child)
