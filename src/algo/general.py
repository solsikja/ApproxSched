import os
import os.path

__infity = 1000


def generate(path, tgff):
    """ Convert structure taskGraph to cplex file """

    for i, graph in enumerate(tgff.graphs):
        fn = path + ".lp"

        if os.path.isfile(fn):
            os.remove(fn)

        file = open(fn, "w")
        gen_graph(file, graph)
        file.close()

    print("OK!")
    return


def gen_graph(file, graph):
    """ Generate a Graph """

    file.write("\\* This is a general scheduling algorithm. *\\ \n")

    for task in graph.tasks.values():
        task.approx = 1

    file.write("\nMinimize\n")
    file.write("obj:\t")
    for leaf in graph.leaves:
        file.write(" + " + leaf.name_start())
        file.write(leaf.cplex_wcet("+", graph.cores))
        file.write("\n")
    file.write("\n")

    file.write("\nSubject To\n")
    file.write("\\* Each task can only run on one processor once *\\ \n")
    for i, task in enumerate(graph.tasks.values()):
        file.write("   etro_" + str(i) + ":\t")
        file.write(task.cplex_d("+", "1", graph.cores))
        file.write(" = 1\n")

    # file.write("\\* Must meet the deadlines *\\ \n")
    # for leaf in graph.leaves:
    #     file.write("   DL_" + leaf.name + ": ")
    #     file.write(" + " + leaf.name_start())
    #     file.write(leaf.cplex_wcet("+", graph.cores))
    #     file.write(" <= " + str(graph.deadline[leaf.name]) + "\n")

    file.write("\\* Must meet the data dependencies *\\ \n")
    count = 0
    for name, task_i in graph.tasks.items():
        if len(task_i.children) == 0:
            continue
        for task_j in task_i.children:
            for core_m in graph.cores:
                for core_k in graph.cores:
                    file.write("   dpd_sp_" + str(count) + ":\t")
                    file.write(" + " + task_i.name_start())
                    file.write(" - " + task_j.name_start())
                    file.write(task_i.cplex_wcet_with_coefficient("+", __infity, [core_m]))
                    # file.write(task_i)
                    # file.write(task_i.cplex_d(" + ", str(__infity), [core_m]))
                    file.write(task_j.cplex_d("+", __infity, [core_k]))
                    file.write(" <= " + str(2 * __infity) + "\n")
                    count += 1

    file.write("\\* Two unrelated tasks must not be executed on the same processor at the same time. *\\ \n")
    count = 0
    for core_m in graph.cores:
        for i, task_i in enumerate(graph.tasks.values()):
            for j, task_j in enumerate(graph.tasks.values()):
                if j <= i:
                    continue
                if (task_i in task_j.children) or (task_j in task_i.children):
                    continue

                file.write("   unr_" + str(count) + "_p:\t")
                file.write(" + " + task_i.name_start())
                file.write(" - " + task_j.name_start())
                file.write(task_i.cplex_wcet_with_coefficient("+", __infity, [core_m]))
                file.write(task_j.cplex_d("+", __infity, [core_m]))
                file.write(" + " + str(__infity) + " " + task_i.name_y(task_j))
                file.write(" <= " + str(3 * __infity) + "\n")

                file.write("   unr_" + str(count) + "_s:\t")
                file.write(" + " + task_j.name_start())
                file.write(" - " + task_i.name_start())
                file.write(task_j.cplex_wcet_with_coefficient("+", __infity, [core_m]))
                file.write(task_i.cplex_d(" + ", __infity, [core_m]))
                file.write(" - " + str(__infity) + " " + task_i.name_y(task_j))
                file.write(" <= " + str(2 * __infity) + "\n")

                count += 1

    file.write("\nBounds\n")
    for i, task in enumerate(graph.tasks.values()):
        file.write(task.name_start() + " >= 0\n")

    file.write("\nBinary\n")
    for i, task in enumerate(graph.tasks.values()):
        for core_m in graph.cores:
            for v in range(task.get_approx_ver()):
                file.write(task.name_assign(core_m, v) + "\n")

    for i, task_i in enumerate(graph.tasks.values()):
        for j, task_j in enumerate(graph.tasks.values()):
            if j <= i:
                continue
            if (task_i in task_j.children) or (task_j in task_i.children):
                continue
            file.write(task_i.name_y(task_j))
            file.write("\n")

    file.write("\nEnd\n")
    file.write("\\* eof *\\")
    return
