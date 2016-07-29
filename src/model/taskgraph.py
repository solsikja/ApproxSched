class Runtime:
    """ Runtime Information """

    def __init__(self):
        self.start = 0
        self.version = 0
        self.core = None


class Task:
    """ Task Structure """

    def __init__(self):
        self.name = ""
        self.type = 0
        self.parents = []
        self.children = []
        self.approx = 0
        self.qualities = []
        self.wcet = []

        self.offline = None     # class Runtime
        self.online = None      # class Runtime
        #
        # self.start = 0
        # self.core = None
        # self.version = 0

    def is_approx(self):
        return self.approx != 1

    def get_approx_ver(self):
        return self.approx

    def get_quality(self, version):
        return self.qualities[version]

    def get_wcet(self, core, version=0):
        if version > self.approx:
            print("Error", self.name, "is not an approximate task.")
            return ""
        return self.wcet[version] * core.speed

    """ for name """
    def name_start(self):
        lst = ["s(", self.name, ")"]
        return "".join(lst)

    def name_assign(self, core, version):
        lst = ["d(p_", str(core.index), ",", self.name, ",v_", str(version), ")"]
        return "".join(lst)

    def name_y(self, task):
        lst = ["y(", self.name, ",", task.name, ")"]
        return "".join(lst)

    """ for cplex output """
    def cplex_wcet(self, operator, cores):
        return self.cplex_wcet_with_coefficient(operator, 0, cores)

    def cplex_wcet_with_coefficient(self, operator, coef, cores):
        operator = operator.strip()
        lst = []
        for core in cores:
            for ver in range(self.approx):
                lst.append(" ")
                lst.append(operator)
                lst.append(" ")
                lst.append(str(self.get_wcet(core, ver) + coef))
                lst.append(" ")
                lst.append(self.name_assign(core, ver))

        return "".join(lst)

    def cplex_wcet_with_multiplier(self, operator, multiplier, cores):
        operator = operator.strip()
        lst = []
        for core in cores:
            for ver in range(self.approx):
                lst.append(" ")
                lst.append(operator)
                lst.append(" ")
                lst.append(str(self.get_wcet(core, ver) * multiplier))
                lst.append(" ")
                lst.append(self.name_assign(core, ver))

        return "".join(lst)

    def cplex_d(self, operator, multiplier, cores):
        operator = operator.strip()
        lst = []
        for core in cores:
            for ver in range(self.approx):
                lst.append(" ")
                lst.append(operator)
                lst.append(" ")
                lst.append(str(multiplier))
                lst.append(" ")
                lst.append(self.name_assign(core, ver))

        return "".join(lst)


class Arc:
    """ Arc Structure """

    def __init__(self):
        self.name = ""
        self.frm = ""
        self.to = ""
        self.type = 0


class Core:
    """ Core Processor Info"""

    def __init__(self):
        self.index = 0
        self.speed = 0


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
        self.cores = []


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
        self.hyperPeriod = 0
        self.graphs = []
        self.tables = []
        self.wcets = []
        self.qualities = []
        self.performances = []
