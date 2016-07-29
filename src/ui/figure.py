import os
import os.path
from ui import svg


class Figure:

    def __init__(self, tgff):
        self.tgff = tgff
        self.graph = tgff.graphs[0]
        """ Constant """
        self.scale = 5
        self.offset = 12 * self.scale
        self.font_size = 4 * self.scale
        self.core_space = 20 * self.scale
        self.box_height = 10 * self.scale
        """ Global Parameters """
        latest_finished_time = 0
        for graph in tgff.graphs:
            for task in graph.leaves:
                tmp = task.offline.start + task.get_wcet(task.offline.core, task.offline.version)
                if tmp > latest_finished_time:
                    latest_finished_time = tmp

        latest_finished_time = latest_finished_time if latest_finished_time > tgff.hyperPeriod else tgff.hyperPeriod

        self.svg_width = int(latest_finished_time) * self.scale + self.offset * 2
        self.svg_height = self.core_space * len(self.graph.cores) + self.offset * 2

        self.width = int(tgff.hyperPeriod) * self.scale
        self.height = self.core_space * len(self.graph.cores)
        self.core_y = []

    def offline(self, path):
        """
        Draw the offline figure
        :param path the file path of the figure
        """

        if os.path.isfile(path):
            os.remove(path)

        _svg = svg.SVG(path, self.scale)
        self.__draw_bg(_svg)
        self.__draw_axis(_svg)

        for task in self.graph.tasks.values():
            self.__draw_task_rect(_svg, task)

        self.__draw_deadline(_svg)

        _svg.save()

    def __draw_bg(self, _svg):
        _svg.draw_rect((0, 0), (self.svg_width, self.svg_height), fill="lightgreen")

    def __draw_axis(self, _svg):
        self.core_y = []
        # draw text
        _svg.draw_text("0", (self.offset - self.font_size/2, self.offset + self.height + self.font_size))
        # x axis
        _svg.draw_line((self.offset, self.offset + self.height),
                  (self.offset + self.width, self.offset + self.height))
        # y axis
        _svg.draw_line((self.offset, self.offset + self.height), (self.offset, self.offset))

        self.core_y.append(self.offset + self.height)
        off_y = self.offset + self.height - self.core_space
        for c in range(len(self.graph.cores) - 1):
            self.core_y.append(off_y)
            _svg.draw_dot_line((self.offset, off_y), (self.offset + self.width, off_y))
            off_y -= self.core_space

    def __draw_deadline(self, _svg):
        _svg.draw_dot_line((self.offset + self.width, self.offset + self.height),
                           (self.offset + self.width, self.offset), stroke=_svg.red)
        _svg.draw_text("HyperPeriod", (self.offset + self.width, self.offset + self.height + self.font_size),
                       fill="red")

        for graph in self.tgff.graphs:
            for name, deadline in graph.deadline.items():
                print(name, deadline)
                _svg.draw_dot_line((self.offset + deadline * self.scale, self.offset + self.height),
                                          (self.offset + deadline * self.scale, self.offset))
                _svg.draw_text(name, (self.offset + deadline * self.scale, self.offset - self.font_size))

    def __draw_task_rect(self, _svg, task):
        offline = task.offline
        x = self.offset + offline.start * self.scale
        y = self.core_y[offline.core.index] - self.box_height
        w = task.get_wcet(offline.core, offline.version) * self.scale
        h = self.box_height

        if task.is_approx():
            _svg.draw_rect((x, y), (w, h), fill="lightgray")
        else:
            _svg.draw_rect((x, y), (w, h))

        _svg.draw_text(task.name, (x, y + self.font_size))
        _svg.draw_text("v:" + str(offline.version), (x, y + self.font_size * 2))
