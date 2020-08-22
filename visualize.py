from datetime import date

import logging
import processing as proc
import matplotlib.pyplot as plt
import sys

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def time_distribution_pie(total_time_dict):
    labels = []
    values = []
    for k, v in total_time_dict.items():
        labels.append(k)
        values.append(v)
    plt.pie(values, labels=labels)
    plt.title(str(date.today()))
    plt.show()


if __name__ == '__main__':
    tasks = proc.get_tasks(sys.argv[1])
    time_dict = proc.get_time_dict(tasks, [])
    time_distribution_pie(time_dict)
