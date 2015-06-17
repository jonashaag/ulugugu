from ulugugu import drawings
from ulugugu.events import Event, ACK, send_event, event_used
from ulugugu.widgets import Object
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


class PositionedChild:
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

  def on_MousePress(self, event, event_ctx):
    child = self.get_first_child_under_cursor(event_ctx)
    self.focused_child = child
    if child:
      response = self.send_event_child(child, event, event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)
      else:
        return ACK

  def send_event_child(self, child, event, event_ctx):
    child_context = event_ctx.clone(
      mouse_x=event_ctx.mouse_x - child.x,
      mouse_y=event_ctx.mouse_y - child.y,
    )
    return send_event(child.inner, event, child_context)

  def forward_event_to_child(self, child, event, event_ctx):
    if child is not None:
      response = self.send_event_child(child, event, event_ctx)
      if event_used(response):
        return self.handle_child_response(response, event_ctx)

  def forward_event_to_focused_child(self, event, event_ctx):
    return self.forward_event_to_child(self.focused_child, event, event_ctx)

  def forward_event_to_child_under_cursor(self, event, event_ctx):
    return self.forward_event_to_child(self.get_first_child_under_cursor(event_ctx), event, event_ctx)

  def get_first_child_under_cursor(self, event_ctx, exclude=()):
    children_under_cursor = self.get_children_at_pos(event_ctx.mouse_x, event_ctx.mouse_y, exclude)
    if children_under_cursor:
      return children_under_cursor[-1]

  def get_children_under_cursor(self, event_ctx, exclude=()):
      return self.get_children_at_pos(event_ctx.mouse_x, event_ctx.mouse_y, exclude)

  def get_children_at_pos(self, x, y, exclude=()):
    return [o for o in self.children if o not in exclude and pt_in_rect(x, y, o.x, o.y, o.inner.width(), o.inner.height())]

  def maybe_drop_child(self, child, event_ctx):
    target = self.get_drop_target(child, event_ctx)
    if target is not None:
      event = ReceiveChild(
        child        = child.inner,
        child_xoff   = event_ctx.mouse_x - child.x,
        child_yoff   = event_ctx.mouse_y - child.y,
      )
      response = self.send_event_child(target, event, event_ctx)
      if event_used(response):
        return target, response
    return None, None

  def get_drop_target(self, child, event_ctx):
    target = self.get_first_child_under_cursor(event_ctx, exclude={child})
    if target is not None and rect_in_rect(child.x, child.y, child.inner.width(), child.inner.height(),
                                           target.x, target.y, target.inner.width(), target.inner.height()):
      return target
