from model import taskgraph


def trim_time_slack(tgff):
    tasks = tgff.tasks
    sorted_tasks = sorted(tasks.values(), key=lambda t: t.offline.start)

    tasks_on_core = []
    max_end_on_core = []

    for core in tgff.cores:
        tl = list(filter(lambda t: t.offline.core.index == core.index, tasks.values()))
        tl.sort(key=lambda t: t.offline.start)
        tasks_on_core.append(tl)
        max_end_on_core.append(0)

    for task in sorted_tasks:
        task.online = taskgraph.Runtime()

        task.online.core = task.offline.core
        task.online.version = task.offline.version

        start_time = task.offline.start
        for parent in task.parents:
            start_time = min(parent.online.end, start_time)
        task.online.start = max(start_time, max_end_on_core[task.online.core.index])
        task.online.end = task.online.start + task.get_wcet(task.online.core, task.online.version) * task.exec

        max_end_on_core[task.online.core.index] = task.online.end

    for task in sorted_tasks:
        print(task.name, task.offline.core.index, task.offline.version, task.offline.start, task.offline.end)

    print()

    for task in sorted_tasks:
        print(task.name, task.online.core.index, task.online.version, task.online.start, task.online.end)

    return
