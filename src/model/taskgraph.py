class Task:
    """ Task Structure """

    def __init__(self):
        self.name = ""

        self.wect = 0
        self.type = 0
        self.parents = []
        self.children = []


class Arc:
    """ Arc Structure """

    def __init__(self):
        self.name = ""
        self.frm = ""
        self.to = ""
        self.type = 0


class TaskGraph:
    """ Task Graph """

    def __init__(self):
        self.name = ""
        self.period = 0
        self.tasks = {}
        self.arcs = []
        self.deadline = {}
        self.roots = []
        self.leaves = []


class Table:
    """ Table in task graph """

    def __init__(self):
        self.type = ""
        self.name = ""
        self.attr = {}
        self.columns = []
        self.values = []


class Tgff:
    """ Tgff Structure """

    def __init__(self):
        self.hyperPeroid = 0
        self.graphs = []
        self.tables = []
