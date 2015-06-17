def pt_in_rect(x, y, rx, ry, rw, rh):
  return rx <= x < rx+rw and ry <= y < ry+rh


def rect_in_rect(x1, y1, w1, h1, x2, y2, w2, h2):
  return x2 <= x1 <= x1 + w1 < x2 + w2 and \
         y2 <= y1 <= y1 + h1 < y2 + h2
