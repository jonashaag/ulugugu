from ulugugu import sdl, drawings, values
from ulugugu.widgets import *
from ulugugu.events import send_event


class ApplicationWidget(object):
 def __init__(self):
   super().__init__(DropArea(), Besides(DropArea(), DropArea()), horizontal_alignment='center')

 def value(self):
   abstraction, *args = super().value()
   return values.Application(abstraction, *args)


class ShowValueWidget(WidgetWrapper):
  def get_drawing(self):
    return drawings.Above(
      drawings.Text(str(self.value())),
      self.child.get_drawing(),
    )


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
# workspace.children.append(PositionedChild(ShowValueWidget(ApplicationWidget()), 100, 100))
workspace.children.append(PositionedChild(ShowValueWidget(StringInput("Test")), 100, 250))
workspace.children.append(PositionedChild(Besides(DropArea(), DropArea()), 100, 250))
workspace.children.append(PositionedChild(Above(DropArea(), DropArea()), 300, 250))
workspace.children.append(PositionedChild(DropArea(), 100, 100))
sdl.main(ProgramState(DragWrapper(workspace)))
