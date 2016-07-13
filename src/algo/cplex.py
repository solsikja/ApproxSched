import os
import os.path
from algo import nameGen

__infity = 1000000


def generate(path, tgff):
    """ Convert structure taskGraph to cplex file """

    for i, graph in enumerate(tgff.graphs):
        fn = path + ".lp"

        if os.path.isfile(fn):
            os.remove(fn)

        file = open(fn, "w")
        gen_graph(file, graph, tgff.tables[0])
        file.close()

    print("OK!")
    return


def gen_graph(file, graph, table):
    """ Generate a Graph """

    proc_num = len(table.columns)-2

    file.write("\\* This is an example. *\\ \n")

    #file.write("\\* minimize( \sum_{t_i \in L} (s_{t_i} + \sum_{p \in P} (wect_{p_m, t_i} \cdot d_{p_m, t_i}))) *\\ \n")
    file.write("\nMinimize\n")
    file.write("obj:\t")

    for leaf in graph.leaves:
        file.write(" + ")
        file.write(nameGen.starttime(leaf))
        for i in range(proc_num):
            file.write(" - " + table.values[leaf.type][i+2] + " " + nameGen.assign(i, leaf))
        file.write("\n")
    file.write("\n")

    file.write("\nSubject To\n")
    file.write("\\* Each task can only run on one processor once *\\ \n")
    for name, task in graph.tasks.items():
        file.write("   etro_" + name + ":\t")
        for m in range(proc_num):
            file.write(" + ")
            file.write(nameGen.assign(m, task))
        file.write(" = 1\n")

    # file.write("\\* Must meet the deadlines *\\ \n")
    # for leaf in graph.leaves:
    #     file.write("   DL_" + leaf.name + ":\t")
    #     file.write(nameGen.starttime(leaf))
    #     for m in range(proc_num):
    #         file.write(" - " + table.values[leaf.type][m + 2] + " " + nameGen.assign(m, leaf) + "\t")
    #     file.write("<=\t" + str(graph.deadline[leaf.name]) + "\n")

    file.write("\\* Must meet the data dependencies *\\ \n")
    count = 0
    for name, task in graph.tasks.items():
        if len(task.children) == 0:
            continue
        for child in task.children:
            for m in range(proc_num):
                for k in range(proc_num):
                    file.write("   dpd_sp_" + str(count) + ":\t")
                    file.write(nameGen.starttime(task) +
                               " - " + nameGen.starttime(child) +
                               " + " + str(__infity) + " " + nameGen.assign(m, task) +
                               " + " + str(__infity) + " " + nameGen.assign(k, leaf) +
                               " <= " + str(2 * __infity - float(table.values[task.type][m + 2]))
                               + "\n")
                    count += 1

    file.write("\\* Two unrelated tasks must not be executed on the same processor at the same time. *\\ \n")
    count = 0
    for m in range(proc_num):
        for i, task_i in enumerate(graph.tasks.values()):
            for j, task_j in enumerate(graph.tasks.values()):
                if j <= i:
                    continue
                if (task_i in task_j.children) or (task_j in task_i.children):
                    continue

                file.write("   unr_" + str(count) + "_p:\t")
                file.write(nameGen.starttime(task_i) +
                           " - " + nameGen.starttime(task_j) +
                           " + " + str(__infity) + " " + nameGen.assign(m, task_i) +
                           " + " + str(__infity) + " " + nameGen.assign(m, task_j) +
                           " + " + str(__infity) + " " + nameGen.y(task_i, task_j) +
                           " <= " + str(3 * __infity - float(table.values[task_i.type][m + 2])) +
                           "\n")

                file.write("   unr_" + str(count) + "_s:\t")
                file.write(nameGen.starttime(task_j) +
                           " - " + nameGen.starttime(task_i) +
                           " + " + str(__infity) + " " + nameGen.assign(m, task_i) +
                           " + " + str(__infity) + " " + nameGen.assign(m, task_j) +
                           " - " + str(__infity) + " " + nameGen.y(task_i, task_j) +
                           " <= " + str(2 * __infity - float(table.values[task_j.type][m + 2])) +
                           " \n")
                count += 1

    file.write("\nBounds\n")
    for i, task in enumerate(graph.tasks.values()):
        file.write(nameGen.starttime(task) + " >= 0\n")

    file.write("\nBinary\n")
    for i, task in enumerate(graph.tasks.values()):
        for m in range(proc_num):
            file.write(nameGen.assign(m, task))
            file.write("\n")
    for i, task_i in enumerate(graph.tasks.values()):
        for j, task_j in enumerate(graph.tasks.values()):
            if j <= i:
                continue
            if (task_i in task_j.children) or (task_j in task_i.children):
                continue
            file.write(nameGen.y(task_i, task_j))
            file.write("\n")

    file.write("\nEnd\n")
    file.write("\\* eof *\\")
    return
