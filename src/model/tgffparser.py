import re
from model import taskgraph
from model import const


class TgffParser:
    """ A parser for tgff files """

    def __init__(self):
        self.tgFlag = False
        self.tblFlag = const.TABLE_OUT
        self.tgff = taskgraph.Tgff()

    def do(self, path):
        file = open(path, "r")

        for line in file:
            match = re.search(r"(.*)}", line)
            if match:
                self.tgFlag = const.TABLE_OUT
                self.tblFlag = False
                continue

            match = re.search(r"@HYPERPERIOD(.*)", line)
            if match:
                self.tgff.hyperPeriod = int(match.group(1))
                # print("Hyperperiod", match.group(1))
                continue

            match = re.search(r"@TASK_GRAPH(.*){", line)
            if match:
                self.tgFlag = True
                tg = taskgraph.TaskGraph();
                tg.name = match.group(1).strip()
                self.tgff.graphs.append(tg)
                # print("Graph title", match.group(1))
                continue

            match = re.search(r"[ ]+PERIOD(.*)", line)
            if match:
                tg.period = int(match.group(1))
                # print("PERIOD", match.group(1))
                continue

            if self.tgFlag:
                match = re.search(r"TASK(.*)TYPE(.*)", line)
                if match:
                    task = taskgraph.Task()
                    task.name = match.group(1).strip()
                    task.type = int(match.group(2))
                    tg.tasks[task.name] = task
                    # print("TASK", match.group(1), end=";")
                    # print("TYPE", match.group(2))
                    continue

                match = re.search(r"ARC(.*)FROM(.*)TO(.*)TYPE(.*)", line)
                if match:
                    arc = taskgraph.Arc()
                    arc.name = match.group(1).strip()
                    arc.frm = match.group(2).strip()
                    arc.to = match.group(3).strip()
                    arc.type = int(match.group(4))

                    tg.arcs.append(arc)
                    # print("ARC", match.group(1), end=";")
                    # print("FROM", match.group(2), end=";")
                    # print("TO", match.group(3), end=";")
                    # print("TYPE", match.group(4))
                    continue

                match = re.search(r"HARD_DEADLINE(.*)ON(.*)AT(.*)", line)
                if match:
                    tg.deadline[match.group(2).strip()] = int(match.group(3).strip())
                    # print("TASK", match.group(2), end=";")
                    # print("DEADLINE", match.group(3))
                    continue

            match = re.search(r"@([^\s]+)( +)([^\s]+) {", line)
            if match:
                self.tblFlag = const.TABLE_ATTR
                table = taskgraph.Table()
                table.type = match.group(1)
                table.name = match.group(3)
                self.tgff.tables.append(table)
                # print("table", match.group(1), match.group(3))
                continue

            if self.tblFlag:
                # match = re.search(r"#-+", line)
                # if match:
                #     self.tblFlag = const.TYPE_ATTR
                #     continue

                match = re.search(r"#(( +)(.*))+", line)
                if match:
                    pattern = re.compile(r'[^\s^#]+', re.DOTALL)
                    lst = pattern.findall(line)
                    if lst[0] == "type":
                        self.tblFlag = const.TYPE_ATTR

                    if self.tblFlag == const.TABLE_ATTR:
                        for item in lst:
                            table.attr[item] = 0
                    elif self.tblFlag == const.TYPE_ATTR:
                        table.columns = lst
                    continue

                match = re.search(r"(( +)([-+]?\d+(\.\d+)?))+", line)
                if match:
                    pattern = re.compile(r"[-+]?\d+\.?\d*", re.DOTALL)
                    lst = pattern.findall(line)
                    # print(lst)
                    if self.tblFlag == const.TABLE_ATTR:
                        for k in table.attr.keys():
                            table.attr[k] = float(lst[0])
                            del lst[0]
                    elif self.tblFlag == const.TYPE_ATTR:
                        tmplst = []
                        for k, val in enumerate(lst):
                            if k < 2:
                                tmplst.append(int(val))
                            else:
                                tmplst.append(float(val))
                        table.values.append(tmplst)
                        # print("tbl", table.name, lst)
                    continue

        file.close()
        return self.tgff

    def generate_graphs(self):

        for table in self.tgff.tables:
            if table.type == "TASK":
                self.tgff.wcets.append(table)
            elif table.type == "QUALITY":
                self.tgff.qualities.append(table)
            elif table.type == "PERFORMANCE":
                self.tgff.performances.append(table)

        # for graph in self.tgff.graphs:
        for g, graph in enumerate(self.tgff.graphs):
            for arc in graph.arcs:
                graph.tasks[arc.frm].children.append(graph.tasks[arc.to])
                graph.tasks[arc.to].parents.append(graph.tasks[arc.frm])

            for t, task in enumerate(graph.tasks.values()):
                if len(task.parents) == 0:
                    graph.roots.append(task)
                if len(task.children) == 0:
                    graph.leaves.append(task)

                if int(self.tgff.wcets[g].values[task.type][2]) != 0:
                    task.approx = len(self.tgff.qualities[g].columns) - 2
                else:
                    task.approx = 1

                task.qualities = self.tgff.qualities[g].values[task.type][2:]
                task.wcet = self.tgff.performances[g].values[task.type][2:]

            for i, s in enumerate(self.tgff.wcets[g].attr.values()):
                core = taskgraph.Core()
                core.index = i
                core.speed = s
                graph.cores.append(core)

        return self.tgff

    def info(self):
        print("HyperPeriod", self.tgff.hyperPeriod)
        for tg in self.tgff.graphs:
            print("-" * 20, "Graph", tg.name, "-" * 20)

            print("Period", tg.period)

            for name, task in tg.tasks.items():
                # print("TASK", task.name, "TYPE", task.type, "PARENTS", list(task.parents), "CHILDREN",
                #       repr(task.children))
                print("TASK", task.name, "TYPE", task.type)
                print("PARENT", end=":")
                for parent in task.parents:
                    print(parent.name, end=";")
                print()
                print("CHILDREN", end=":")
                for child in task.children:
                    print(child.name, end=";")
                print()

            for arc in tg.arcs:
                print("ARC", arc.name, "FROM", arc.frm, "TO", arc.to, "TYPE",arc.type)

            for k, v in tg.deadline.items():
                print("DEADLINE", k, v)

        for t in self.tgff.tables:
            print("-" * 20, "Table", t.type, t.name, "-" * 20)
            for k, v in t.attr.items():
                print("attr", k, v)
            print(t.columns)
            for v in t.values:
                print(v)
