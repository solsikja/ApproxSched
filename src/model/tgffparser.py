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
                job = taskgraph.Job();
                job.name = match.group(1).strip()
                self.tgff.jobs.append(job)
                # print("Graph title", match.group(1))
                continue

            match = re.search(r"[ ]+PERIOD(.*)", line)
            if match:
                job.period = int(match.group(1))
                # print("PERIOD", match.group(1))
                continue

            if self.tgFlag:
                match = re.search(r"TASK(.*)TYPE(.*)", line)
                if match:
                    task = taskgraph.Task()
                    task.name = match.group(1).strip()
                    task.type = int(match.group(2))
                    job.tasks[task.name] = task
                    continue

                match = re.search(r"ARC(.*)FROM(.*)TO(.*)TYPE(.*)", line)
                if match:
                    arc = taskgraph.Arc()
                    arc.name = match.group(1).strip()
                    arc.frm = match.group(2).strip()
                    arc.to = match.group(3).strip()
                    arc.type = int(match.group(4))

                    job.arcs.append(arc)
                    continue

                match = re.search(r"HARD_DEADLINE(.*)ON(.*)AT(.*)", line)
                if match:
                    job.deadlines[match.group(2).strip()] = int(match.group(3).strip())
                    self.tgff.deadlines[match.group(2).strip()] = int(match.group(3).strip())
                    continue

            match = re.search(r"@([^\s]+)( +)([^\s]+) {", line)
            if match:
                self.tblFlag = const.TABLE_ATTR
                table = taskgraph.Table()
                table.type = match.group(1)
                table.name = match.group(3)
                self.tgff.tables.append(table)
                continue

            if self.tblFlag:
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
                    continue

        file.close()
        return self.tgff

    def generate_graphs(self):

        tgff = self.tgff

        for table in tgff.tables:
            if table.type == "TASK":
                tgff.approx = table
            elif table.type == "QUALITY":
                tgff.quality = table
            elif table.type == "PERFORMANCE":
                tgff.performance = table

        for job in tgff.jobs:
            for arc in job.arcs:
                job.tasks[arc.frm].children.append(job.tasks[arc.to])
                job.tasks[arc.to].parents.append(job.tasks[arc.frm])

            for task in job.tasks.values():
                tgff.tasks[task.name] = task
                if len(task.parents) == 0:
                    job.roots.append(task)
                    tgff.roots.append(task)
                if len(task.children) == 0:
                    job.leaves.append(task)
                    tgff.leaves.append(task)
                if int(tgff.approx.values[task.type][2]) != 0:
                    task.approx = len(tgff.quality.columns) - 2
                else:
                    task.approx = 1
                task.qualities = tgff.quality.values[task.type][2:]
                task.wcet = tgff.performance.values[task.type][2:]

        for i, s in enumerate(tgff.performance.attr.values()):
            core = taskgraph.Core()
            core.index = i
            core.speed = s
            tgff.cores.append(core)

        return tgff

    def info(self):
        print("HyperPeriod", self.tgff.hyperPeriod)
        for tg in self.tgff.graphs:
            print("-" * 20, "Graph", tg.name, "-" * 20)

            print("Period", tg.period)

            for task in tg.tasks.values():
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
