import db


class Task:
    DUR_LIMIT = 12 * 60 * 60
    SLEEP_DUR_LIMIT = 15 * 60 * 60

    def __init__(self, name, start_time, next_task=None):
        self.name = name
        self.start_time = start_time
        if next_task is None:
            self.duration = 360
        else:
            self.duration = next_task.start_time - self.start_time
        if self.duration < 0:
            raise ValueError('Duration cannot be negative: ' + str(self))
        if self.name == 'sleeping' and self.duration > self.SLEEP_DUR_LIMIT:
            self.duration = 8 * 60 * 60
        elif self.duration > self.DUR_LIMIT:
            self.duration = 60 * 60

    def __str__(self):
        return 'Task({}, {}, {})'.format(self.name,
                                         self.start_time,
                                         self.format_duration())

    def format_duration(self):
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        return f'{h:d}:{m:02d}'


def get_tasks(db_path):
    db_tasks = db.get_all_tasks(db_path)
    if len(db_tasks) == 0:
        return []
    end = db_tasks[-1]
    tasks = [Task(end['name'], end['startTime'])]

    for i in reversed(range(0, len(db_tasks) - 1)):
        c = db_tasks[i]
        tasks.append(Task(c['name'], c['startTime'], tasks[-1]))
    return tasks


def get_time_dict(tasks, ignore_list=None, time_interval=None):
    if ignore_list is None:
        ignore_list = []
    time_dict = {}
    for task in tasks:
        if task.name in ignore_list:
            continue
        if task.name not in time_dict:
            time_dict[task.name] = 0
        time_dict[task.name] += task.duration
    return time_dict
