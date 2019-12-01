#!/usr/bin/env python3
from argparse import ArgumentParser
import time
from multiprocessing import cpu_count, Process, Queue
from queue import Empty

from lxml.html import fromstring


def parse_cpu_info(key):
    try:
        with open('/proc/cpuinfo') as inp:
            for line in inp:
                if line.startswith(key):
                    return line.split(':', 1)[1].strip()
    except IOError:
        pass
    return 'NA'


def thread_parser(data, taskq):
    while True:
        try:
            taskq.get_nowait()
        except Empty:
            return
        else:
            dom = fromstring(data)
            assert 'reddit' in dom.xpath('//title')[0].text


def main():
    parser = ArgumentParser()
    parser.add_argument('-n', '--tasks-number', type=int, default=10)
    opts = parser.parse_args()
    total_num_cpu = cpu_count()
    with open('data/reddit.html') as inp:
        data = inp.read()

    taskq = Queue()
    for _ in range(opts.tasks_number):
        taskq.put(None)

    num_cpu_used = set()
    history = []
    #for div in (None, 0.25, 5, 0.75, 1):
    for div in [None]:
        if div is None:
            num_cpu = 1
        else:
            num_cpu = round(total_num_cpu * div)
        if num_cpu not in num_cpu_used:
            num_cpu_used.add(num_cpu)
            print('Using %d CPUs' % num_cpu, end='')
            started = time.time()
            pool = []
            for _ in range(2):
                proc = Process(target=thread_parser, args=[data, taskq])
                proc.start()
                pool.append(proc)
            [x.join() for x in pool]
            elapsed = time.time() - started
            print('%.2f' % elapsed)
            history.append((num_cpu, elapsed))
    model_name = parse_cpu_info('model name')
    cache_size = parse_cpu_info('cache size')
    print('CPU : %s, cache=%s' % (model_name, cache_size))
    print('Time:', ', '.join('%d=%.2f' % x for x in history))

if __name__ == '__main__':
    main()
