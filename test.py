from ulugugu import sdl, drawings, keys
from ulugugu.widgets import *
from ulugugu.events import Event, ACK, send_event, event_used


class DropArea(Workspace):
  def draw(self, ctx):
    super().draw(ctx)
    drawings.Rectangle(
      width=self.width(),
      height=self.height(),
      color=(0.7, 0.9, 0.7),
      fill='stroke',
    ).draw(ctx)

  def on_DragStop(self, event, event_ctx):
    if self.children:
      self.children[0].x = 0
      self.children[0].y = 0


class BesidesWidget(Container):
  def __init__(self, left, right):
    self.width = lambda: left.width() + right.width()
    self.height = lambda: max(left.height(), right.height())
    self.focused_child = None
    self.children = [PositionedChild(left, 0, 0),
                     PositionedChild(right, left.width(), 0)]

  def update_child_positions(self):
    self.children[1].x = self.children[0].inner.width()

  def handle_child_response(self, response, event_ctx):
    self.update_child_positions()
    if response in {None, ACK}:
      return response
    else:
      if not isinstance(response, UnparentChild):
        raise TypeError("Don't know how to deal with child response %s" % response)
      return response.clone(former_parent=self)

  on_KeyPress     = Container.forward_event_to_focused_child
  on_Drag         = Container.forward_event_to_focused_child
  on_DragStart    = Container.forward_event_to_focused_child
  on_DragStop     = Container.forward_event_to_focused_child
  on_MouseRelease = Container.forward_event_to_focused_child
  on_MouseMove    = Container.forward_event_to_child_under_cursor

  def on_ReceiveChild(self, event, event_ctx):
    target, child_response = self.maybe_drop_child(PositionedChild(event.child, event_ctx.mouse_x - event.child_xoff, event_ctx.mouse_y - event.child_yoff), event_ctx)
    if target is not None:
      self.focused_child = target
      return self.handle_child_response(child_response, event_ctx)


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
workspace.add_child(Workspace(200, 200), 400, 400)
sdl.main(ProgramState(DragWrapper(workspace)))
