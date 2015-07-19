import abc
from ulugugu import drawings, vec2
from ulugugu.events import ACK, send_event, event_used
from ulugugu.widgets import Widget, WidgetWrapper
from ulugugu.widgets.drag import UnparentChild, ReceiveChild
from ulugugu.utils import cursor_over_drawing
from functional import foldl


class PositionedChild(WidgetWrapper):
  def __init__(self, child, position):
    super().__init__(child)
    self.position = position

  def move(self, newpos):
    self.position = newpos

  def move_relative(self, offset):
    self.position = vec2.add(self.position, offset)


class Container(Widget):
  can_move_children = True

  def __init__(self, children=None):
    self.focused_child = None
    self.children = children or []
    self.update_child_positions()

  def get_drawing(self):
    def add_child_drawing(drawing, child):
      child_drawing = child.get_drawing()
      if child is self.focused_child:
        l, t, _, _ = child_drawing.boundingbox
        border = drawings.Rectangle(
          (child_drawing.width + 4, child_drawing.height + 4),
          (0.3, 0.3, 0.8),
          fill='stroke'
        ).move((l - 2, t - 2))
        child_drawing = drawings.Atop(border, child_drawing)
      return drawings.Atop(child_drawing.move(child.position), drawing)

    return foldl(add_child_drawing, self.children, drawings.Empty())

  @abc.abstractmethod
  def update_child_positions(self):
    pass

  @abc.abstractmethod
  def can_add_child(self, positioned_child):
    pass

  def forward_event_to_focused_child(self, event, event_ctx):
    return self.forward_event_to_child(self.focused_child, event, event_ctx)

  def forward_event_to_child_under_cursor(self, event, event_ctx):
    return self.forward_event_to_child(self.get_child_under_cursor(event_ctx), event, event_ctx)

  on_KeyPress_default = forward_event_to_focused_child
  on_MouseRelease     = forward_event_to_focused_child
  on_DragStart        = forward_event_to_focused_child
  on_DragStop         = forward_event_to_child_under_cursor
  on_MouseMove        = forward_event_to_child_under_cursor

  def on_MousePress(self, event, event_ctx):
    child = self.get_child_under_cursor(event_ctx)
    self.focused_child = child
    if child:
      response = self.send_event_child(child, event, event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
      else:
        return ACK

  def on_ReceiveChild(self, event, event_ctx):
    positioned_child = PositionedChild(
      event.child,
      vec2.sub(event_ctx.mouse_position, event.child_offset),
    )

    # Try drop on child
    target, child_response = self.maybe_drop_child(positioned_child, event_ctx)
    if target is not None:
      self.focused_child = target
      return self.handle_child_response(child_response, event_ctx)

    # Try drop on self
    if self.can_add_child(positioned_child):
      self.children.append(positioned_child)
      self.focused_child = positioned_child
      return ACK

  def on_Drag(self, event, event_ctx):
    if self.focused_child is None:
      return

    response = self.send_event_child(self.focused_child, event, event_ctx)
    if event_used(response):
      return self.handle_child_response(response, event_ctx)

    if not self.can_move_children:
      return

    self.raise_child(self.focused_child)
    self.focused_child.move_relative(event.relative_movement)

    # Cursor out of bounding box?
    if not cursor_over_drawing(self.get_drawing(), event_ctx):
      return self.unparent_child(event_ctx, self.focused_child)

    target, child_response = self.maybe_drop_child(self.focused_child, event_ctx)
    if target is not None:
      self.children.remove(self.focused_child)
      self.focused_child = target
      return self.handle_child_response(child_response, event_ctx)

    return ACK

  def handle_child_response(self, response, event_ctx):
    if response is None:
      return
    else:
      self.update_child_positions()
      if response is ACK:
        return ACK
      elif isinstance(response, UnparentChild):
        positioned_child = PositionedChild(
          response.child,
          vec2.sub(event_ctx.mouse_position, response.child_offset),
        )

        if self.can_add_child(positioned_child):
          self.children.append(positioned_child)
          self.focused_child = positioned_child
          return ACK
        else:
          return response.clone(former_parent=self)
      else:
        raise TypeError("Don't know how to deal with child response %s" % response)

  def unparent_child(self, event_ctx, child):
    event = UnparentChild(
      former_parent = self,
      child         = child.child,
      child_offset  = vec2.sub(event_ctx.mouse_position, child.position),
    )
    self.children.remove(self.focused_child)
    self.focused_child = None
    return event

  def raise_child(self, child):
    """Push 'child' to top of draw stack"""
    self.children.remove(child)
    self.children.append(child)

  def send_event_child(self, child, event, event_ctx):
    return send_event(child.child, event.for_child(child.position), event_ctx.for_child(child.position))

  def forward_event_to_child(self, child, event, event_ctx):
    if child is not None:
      response = self.send_event_child(child, event, event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)

  def get_child_under_cursor(self, event_ctx, exclude=()):
    for child in reversed(self.children):
      if child in exclude:
        continue
      if cursor_over_drawing(child.get_drawing(), event_ctx, offset=child.position):
        return child

  def maybe_drop_child(self, child, event_ctx):
    target = self.get_child_under_cursor(event_ctx, exclude={child})
    if target is not None:
      event = ReceiveChild(
        child        = child.child,
        child_offset = vec2.sub(event_ctx.mouse_position, child.position),
      )
      response = self.send_event_child(target, event, event_ctx)
      if event_used(response):
        return target, response
    return None, None
