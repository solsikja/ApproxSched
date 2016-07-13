def starttime(task):
    lst = ["s(", task.name, ")"]
    return "".join(lst)


def assign(processor, task):
    lst = ["d(p_", str(processor), ",", task.name, ")"]
    return "".join(lst)


def y(task_i, task_j):
    lst = ["y(", task_i.name, ",", task_j.name, ")"]
    return "".join(lst)
