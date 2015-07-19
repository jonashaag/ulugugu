from ulugugu import vec2


def cursor_over_drawing(drawing, event_ctx, offset=(0, 0)):
  l, t, r, b = drawing.boundingbox
  return vec2.le((l, t), vec2.sub(event_ctx.mouse_position, offset), (r, b))
