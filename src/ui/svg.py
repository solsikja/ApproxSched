import svgwrite


class SVG:
    """ A light package class for svgwrite """

    red = svgwrite.rgb(255, 0, 0)
    black = svgwrite.rgb(0, 0, 0)

    _dft_font_size = 4
    _dft_fill = "white"
    _dft_stroke = black  # black
    _dft_stroke_dasharray = "2,2"

    def __init__(self, path, scale):
        self.dwg = svgwrite.Drawing(path, profile='full')
        self.scale = scale

    def save(self):
        self.dwg.save()

    def draw_text(self, text, insert, fill="black", font_size=_dft_font_size):
        text = self.dwg.text(text, insert=insert,  fill=fill, font_size=str(font_size * self.scale) + "px")
        self.dwg.add(text)

    def draw_line(self, start, end, stroke=_dft_stroke):
        line = self.dwg.line(start, end, stroke=stroke)
        self.dwg.add(line)

    def draw_dot_line(self, start, end, stroke=_dft_stroke, stroke_dasharray=_dft_stroke_dasharray):
        dot_line = self.dwg.line(start, end, stroke=stroke, stroke_dasharray=stroke_dasharray)
        self.dwg.add(dot_line)

    def draw_rect(self, point, size, stroke=_dft_stroke, fill=_dft_fill):
        rect = self.dwg.rect(point, size, stroke=stroke, fill=fill)
        self.dwg.add(rect)

