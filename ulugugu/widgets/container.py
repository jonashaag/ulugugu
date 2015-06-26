import abc
from ulugugu import drawings
from ulugugu.events import Event, ACK, send_event, event_used
from ulugugu.widgets import Widget, WidgetWrapper
from ulugugu.utils import pt_in_rect, rect_in_rect


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


class PositionedChild(WidgetWrapper):
  def __init__(self, child, x=0, y=0):
    super().__init__(child)
    self.x = x
    self.y = y

  def move(self, x, y):
    self.x = x
    self.y = y

  def move_relative(self, xoff, yoff):
    self.x += xoff
    self.y += yoff


class Container(Widget):
  can_move_children = True

  def __init__(self, children=None):
    self.focused_child = None
    self.children = children or []
    self.update_child_positions()

  @abc.abstractmethod
  def update_child_positions(self):
    pass

  @abc.abstractmethod
  def can_add_child(self, positioned_child):
    pass

  def forward_event_to_focused_child(self, event, event_ctx):
    return self.forward_event_to_child(self.focused_child, event, event_ctx)

  def forward_event_to_child_under_cursor(self, event, event_ctx):
    return self.forward_event_to_child(self.get_first_child_under_cursor(event_ctx), event, event_ctx)

  on_KeyPress_default = forward_event_to_focused_child
  on_MouseRelease     = forward_event_to_focused_child
  on_DragStart        = forward_event_to_focused_child
  on_MouseMove        = forward_event_to_child_under_cursor

  def on_MousePress(self, event, event_ctx):
    child = self.get_first_child_under_cursor(event_ctx)
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
      event_ctx.mouse_x - event.child_xoff,
      event_ctx.mouse_y - event.child_yoff,
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
    self.focused_child.move_relative(event.xrel, event.yrel)

    # Cursor out of bounding box?
    if not pt_in_rect(event_ctx.mouse_x, event_ctx.mouse_y, 0, 0, self.width(), self.height()):
      return self.unparent_child(event_ctx, self.focused_child)

    target, child_response = self.maybe_drop_child(self.focused_child, event_ctx)
    if target is not None:
      self.children.remove(self.focused_child)
      self.focused_child = target
      return self.handle_child_response(child_response, event_ctx)

    return ACK

  def on_DragStop(self, event, event_ctx):
    for child in self.children:
      child.move(
        min(self.width() - child.width(), max(0, child.x)),
        min(self.height() - child.height(), max(0, child.y))
      )
    return self.forward_event_to_child_under_cursor(event, event_ctx)

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
          event_ctx.mouse_x - response.child_xoff,
          event_ctx.mouse_y - response.child_yoff
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
      child_xoff    = event_ctx.mouse_x - child.x,
      child_yoff    = event_ctx.mouse_y - child.y,
    )
    self.children.remove(self.focused_child)
    self.focused_child = None
    return event

  def raise_child(self, child):
    """Push 'child' to top of draw stack"""
    self.children.remove(child)
    self.children.append(child)

  def draw(self, ctx):
    for child in self.children:
      with ctx:
        ctx.translate(child.x, child.y)
        with ctx:
          child.draw(ctx)
        if self.focused_child is child:
          border = drawings.Rectangle(
            width=child.width()+4,
            height=child.height()+4,
            color=(0.3, 0.3, 0.8),
            fill='stroke'
          ).move(-2, -2)
          border.draw(ctx)

  def send_event_child(self, child, event, event_ctx):
    child_context = event_ctx.clone(
      mouse_x=event_ctx.mouse_x - child.x,
      mouse_y=event_ctx.mouse_y - child.y,
    )
    return send_event(child, event, child_context)

  def forward_event_to_child(self, child, event, event_ctx):
    if child is not None:
      response = self.send_event_child(child, event, event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)

  def get_first_child_under_cursor(self, event_ctx, exclude=()):
    children_under_cursor = self.get_children_at_pos(event_ctx.mouse_x, event_ctx.mouse_y, exclude)
    if children_under_cursor:
      return children_under_cursor[-1]

  def get_children_under_cursor(self, event_ctx, exclude=()):
      return self.get_children_at_pos(event_ctx.mouse_x, event_ctx.mouse_y, exclude)

  def get_children_at_pos(self, x, y, exclude=()):
    return [o for o in self.children if o not in exclude and pt_in_rect(x, y, o.x, o.y, o.width(), o.height())]

  def maybe_drop_child(self, child, event_ctx):
    target = self.get_drop_target(child, event_ctx)
    if target is not None:
      event = ReceiveChild(
        child        = child.child,
        child_xoff   = event_ctx.mouse_x - child.x,
        child_yoff   = event_ctx.mouse_y - child.y,
      )
      response = self.send_event_child(target, event, event_ctx)
      if event_used(response):
        return target, response
    return None, None

  def get_drop_target(self, child, event_ctx):
    target = self.get_first_child_under_cursor(event_ctx, exclude={child})
    if target is not None and pt_in_rect(event_ctx.mouse_x, event_ctx.mouse_y, target.x, target.y, target.width(), target.height()):
      return target
