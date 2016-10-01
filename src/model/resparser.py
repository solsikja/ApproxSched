import re
from model import taskgraph

class ResParser:
    """ A parser for res files"""

    def __init__(self, tgff):
        self.tgff = tgff
        self.flag = False

    def do(self, path):
        file = open(path, "r")
        pname = ""
        for line in file:

            if not self.flag:
                match = re.search(r" +No\. +Column name\.*", line)
                if match:
                    self.flag = True
                    continue

                continue

            match = re.search(r" *Integer feasibility conditions:", line)
            if match:
                self.flag = False
                continue

            match = re.search(r"^\s+(\d+) +(\S+)$", line)
            if match:
                pname = match.group(2)
                # print(pname, end=" ")
                continue

            match = re.search(r"^\s+\*\s+(\S+)", line)
            if match:
                # print(match.group(1))
                self.deal_with_result(pname, match.group(1))
                continue

            match = re.search(r"^\s+\d+\s+(\S+) \*?\s+(\S+)", line)
            if match:
                # print(match.group(1), match.group(2))
                self.deal_with_result(match.group(1), match.group(2))
                continue

        file.close()
        self.generate_time()

    def deal_with_result(self, pn, result):
        tasks = self.tgff.tasks
        if pn.startswith("d"):
            match = re.search(r"d\(p_(\d+),(\S+),v_(\d+)\)", pn)
            if match:
                if int(result) == 1:
                    if not tasks[match.group(2)].offline:
                        tasks[match.group(2)].offline = taskgraph.Runtime()
                    tasks[match.group(2)].offline.core = self.get_core(int(match.group(1)))
                    tasks[match.group(2)].offline.version = int(match.group(3))
        elif pn.startswith("s"):
            match = re.search(r"s\((\S+)\)", pn)
            if match:
                # print("t:", match.group(1), "result:", result)
                if not tasks[match.group(1)].offline:
                    tasks[match.group(1)].offline = taskgraph.Runtime()
                tasks[match.group(1)].offline.start = float(result)
        return

    def get_core(self, core_index):
        cores = self.tgff.cores
        for core in cores:
            if core.index == core_index:
                return core
        return None

    def generate_time(self):
        for task in self.tgff.tasks.values():
            task.offline.end = task.offline.start + task.get_wcet(task.offline.core, task.offline.version)
            task.online = taskgraph.Runtime()
            task.online.core = task.offline.core
            task.online.version = task.offline.version
            task.online.start = task.offline.start
            task.online.end = task.online.start + task.get_wcet(task.online.core, task.online.version) * task.exec

