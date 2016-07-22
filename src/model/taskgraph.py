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

    def is_approx(self):
        return self.approx != 0

    def get_approx_ver(self):
        return self.approx

    def get_quality(self, version):
        return self.qualities[version]

    def get_wcet(self, core, version=0):
        if version > self.approx:
            print("Error", self.name, "is not an approximate task.")
            return ""
        return str(float(self.wcet[version]) * float(core.speed))

    """ for name """
    def name_start(self):
        lst = ["s(", self.name, ")"]
        return "".join(lst)

    def name_assign(self, core):
        lst = ["d(p_", str(core.index), ",", self.name, ")"]
        return "".join(lst)

    def name_assign_approx(self, core, version):
        lst = ["d(p_", str(core.index), ",", self.name, ",v_", str(version), ")"]
        return "".join(lst)

    def name_y(self, task):
        lst = ["y(", self.name, ",", task.name, ")"]
        return "".join(lst)

    """ for cplex output """
    def cplex_wcet(self, operator, cores):
        return self.cplex_wcet_with_coefficient(operator, "0", cores)

    def cplex_wcet_with_coefficient(self, operator, coef, cores):
        operator = operator.strip()
        coef = coef.strip()
        lst = []
        for core in cores:
            if self.is_approx():
                for ver in range(self.approx):
                    lst.append(" ")
                    lst.append(operator)
                    lst.append(" ")
                    lst.append(str(float(self.get_wcet(core, ver)) + float(coef)))
                    lst.append(" ")
                    lst.append(self.name_assign_approx(core, ver))
            else:
                lst.append(" ")
                lst.append(operator)
                lst.append(" ")
                lst.append(str(float(self.get_wcet(core)) + float(coef)))
                lst.append(" ")
                lst.append(self.name_assign(core))

        return "".join(lst)

    def cplex_d(self, operator, multiplier, cores):
        operator = operator.strip()
        multiplier = multiplier.strip()
        lst = []
        for core in cores:
            if self.is_approx():
                for ver in range(self.approx):
                    lst.append(" ")
                    lst.append(operator)
                    lst.append(" ")
                    lst.append(multiplier)
                    lst.append(" ")
                    lst.append(self.name_assign_approx(core, ver))
            else:
                lst.append(" ")
                lst.append(operator)
                lst.append(" ")
                lst.append(multiplier)
                lst.append(" ")
                lst.append(self.name_assign(core))

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

    # def core_num(self):
    #     return len(self.wcets[0].attr)
    #
    # def core_speed(self, core):
    #     return self.wcets[0].attr["core_v" + core]
    #
    # def is_approx(self, task):
    #     return self.wcets[0].values[task.type][3] != 0
    #
    # def approx_ver_num(self):
    #     return len(self.qualities[0].columns) - 2
    #
    # def get_wcet(self, core, task):
    #     if self.is_approx(self, task):
    #         print("Error:", task.name, "is an approximate task.")
    #         return ""
    #
    #     wcet = self.wcets[0].values[task.type][2]
    #     speed = self.core_speed(self, core)
    #     return str(float(wcet) * float(speed))
    #
    # def get_approx_wcet(self, core, task, version):
    #     if not self.is_approx(self, task):
    #         print("Error:", task.name, "is not an approximate task.")
    #         return ""
    #
    #     wcet = self.performances[0].values[task.type][version + 2]
    #     speed = self.core_speed(self, core)
    #     return str(float(wcet) * float(speed))
