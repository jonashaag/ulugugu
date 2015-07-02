from ulugugu import sdl, drawings, values
from ulugugu.widgets import Widget, WidgetWrapper, Above, Besides, ChangeDrawing
from ulugugu.widgets.container import PositionedChild
from ulugugu.widgets.workspace import Workspace
from ulugugu.widgets.droparea import DropArea
from ulugugu.widgets.input import StringInput
from ulugugu.widgets.drag import DragWrapper
from ulugugu.events import send_event


class ApplicationWidget(Above):
 def __init__(self):
   super().__init__(DropArea(), Besides(DropArea(), DropArea()))

 def value(self):
   abstraction, args = super().value()
   return values.Application(abstraction, *args)


class ShowValueWidget(ChangeDrawing):
  def get_drawing(self):
    return drawings.Above(
      drawings.Text(str(self.child.value())),
      self.child.get_drawing(),
    )

  def get_child_position(self):
    return self.get_drawing().get_bottom_drawing_position()


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
      self.rootobj.get_drawing().draw(ctx)


workspace = Workspace(700, 500)
workspace.children.append(PositionedChild(ShowValueWidget(ApplicationWidget()), 100, 100))
workspace.children.append(PositionedChild(ShowValueWidget(StringInput("Test")), 100, 250))
workspace.children.append(PositionedChild(Besides(DropArea(), DropArea()), 100, 250))
workspace.children.append(PositionedChild(Above(DropArea(), DropArea()), 300, 250))
workspace.children.append(PositionedChild(DropArea(), 100, 100))
sdl.main(ProgramState(DragWrapper(workspace)))
