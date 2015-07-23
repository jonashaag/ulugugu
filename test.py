from ulugugu import sdl, drawings, values
from ulugugu.widgets import *
from ulugugu.widgets.workspace import Workspace
from ulugugu.widgets.droparea import DropArea
from ulugugu.widgets.input import StringInput
from ulugugu.widgets.static import StaticWidget
from ulugugu.widgets.drag import DragWrapper
from ulugugu.widgets.debug import ChangingSizeWidget, MouseoverWidget, DebugBoundingBox
from ulugugu.events import send_event


class ApplicationWidget(Above):
  def __init__(self):
    super().__init__(
      Align(DropArea(), (0.5, None)),
      Align(Besides(DropArea(), DropArea()), (0.5, None)),
    )

  def value(self):
    abstraction, args = super().value()
    return values.Application(abstraction, *args)


class ProgramState:
  def __init__(self, rootobj):
    self.rootobj = Align(rootobj, (0, 0))

  def handle_event(self, event, event_ctx):
    if hasattr(event, 'key') and event.key == 'CHAR_R':
      exit(42)
    return send_event(self.rootobj, event, event_ctx)

  def draw(self, ctx):
    with ctx:
      ctx.set_source_rgb(1,1,1)
      ctx.paint()
    with ctx:
      self.rootobj.get_drawing().draw(ctx)


workspace = Workspace(700, 500)
workspace.add_child(ApplicationWidget(), (100, 100))
workspace.add_child(StaticWidget(drawings.Rectangle((100,10), (0,0,0))), (200, 100))
sdl.main(ProgramState(DragWrapper(workspace)))

#sdl.main(ProgramState(Above(ChangingSizeWidget(), MouseoverWidget())))
