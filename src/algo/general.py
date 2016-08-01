import os
import os.path

__infity = 1000


def generate(path, tgff):
    """ Convert structure taskGraph to cplex file """
    if os.path.isfile(path):
        os.remove(path)

    file = open(path, "w")
    gen_graph(file, tgff)
    file.close()

    print("OK!")
    return


def gen_graph(file, tgff):
    """ Generate a Graph """

    file.write("\\* This is a general scheduling algorithm. *\\ \n")

    for task in tgff.tasks.values():
        task.approx = 1

    file.write("\nMinimize\n")
    file.write("obj:\t")
    for leaf in tgff.leaves:
        file.write(" + " + leaf.name_start())
        file.write(leaf.cplex_wcet("+", tgff.cores))
        file.write("\n")
    file.write("\n")

    file.write("\nSubject To\n")
    file.write("\\* Each task can only run on one processor once *\\ \n")
    for i, task in enumerate(tgff.tasks.values()):
        file.write("   etro_" + str(i) + ":\t")
        file.write(task.cplex_d("+", "1", tgff.cores))
        file.write(" = 1\n")

    file.write("\\* Must meet the data dependencies *\\ \n")
    count = 0
    for task_i in tgff.tasks.values():
        if len(task_i.children) == 0:
            continue
        for task_j in task_i.children:
            for core_m in tgff.cores:
                for core_k in tgff.cores:
                    file.write("   dpd_sp_" + str(count) + ":\t")
                    file.write(" + " + task_i.name_start())
                    file.write(" - " + task_j.name_start())
                    file.write(task_i.cplex_wcet_with_coefficient("+", __infity, [core_m]))
                    file.write(task_j.cplex_d("+", __infity, [core_k]))
                    file.write(" <= " + str(2 * __infity) + "\n")
                    count += 1

    file.write("\\* Two unrelated tasks must not be executed on the same processor at the same time. *\\ \n")
    count = 0
    for core_m in tgff.cores:
        for i, task_i in enumerate(tgff.tasks.values()):
            for j, task_j in enumerate(tgff.tasks.values()):
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
    for task in tgff.tasks.values():
        file.write(task.name_start() + " >= 0\n")

    file.write("\nBinary\n")
    for task in tgff.tasks.values():
        for core_m in tgff.cores:
            for v in range(task.get_approx_ver()):
                file.write(task.name_assign(core_m, v) + "\n")

    for i, task_i in enumerate(tgff.tasks.values()):
        for j, task_j in enumerate(tgff.tasks.values()):
            if j <= i:
                continue
            if (task_i in task_j.children) or (task_j in task_i.children):
                continue
            file.write(task_i.name_y(task_j))
            file.write("\n")

    file.write("\nEnd\n")
    file.write("\\* eof *\\")
    return
