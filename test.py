from ulugugu import sdl, drawings, values
from ulugugu.widgets import Widget, WidgetWrapper, Atop, Above, Besides
from ulugugu.widgets.container import PositionedChild
from ulugugu.widgets.workspace import Workspace
from ulugugu.widgets.droparea import DropArea
from ulugugu.widgets.input import StringInput
from ulugugu.widgets.static import StaticWidget
from ulugugu.widgets.drag import DragWrapper
from ulugugu.widgets.debug import DebugBoundingBox
from ulugugu.events import send_event


class ApplicationWidget(Above):
  def __init__(self):
    super().__init__(
      DropArea(),
      Besides(DropArea(), DropArea()),
      horizontal_alignment=0.5
    )

  def value(self):
    abstraction, args = super().value()
    return values.Application(abstraction, *args)


class ProgramState:
  def __init__(self, rootobj):
    self.rootobj = rootobj

  def handle_event(self, event, event_ctx):
    return send_event(self.rootobj, event, event_ctx)

  def draw(self, ctx):
    with ctx:
      ctx.set_source_rgb(1,1,1)
      ctx.paint()
    with ctx:
      self.rootobj.get_drawing().align(0, 0).draw(ctx)


workspace = Workspace(700, 500)
workspace.children.append(PositionedChild(DebugBoundingBox(ApplicationWidget()), (0, 0)))
sdl.main(ProgramState(DragWrapper(workspace)))
