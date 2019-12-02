#!/usr/bin/env python3
"""
Most of calls of print function in this code
use double space at end of output string. It is to force
markdown parser to enter new line, in case you want to put
output of test into markdown document.

See results of tests runned on different machines here:
https://github.com/lorien/lxmlbench/wiki/Test-Results
"""
from argparse import ArgumentParser
import time
from multiprocessing import cpu_count, Process
from urllib.request import urlopen
import os

from lxml.html import fromstring

NUM_DOCUMENTS = 1000

def parse_cpu_info(key):
    try:
        with open('/proc/cpuinfo') as inp:
            for line in inp:
                if line.startswith(key):
                    return line.split(':', 1)[1].strip()
    except IOError:
        pass
    return 'NA'


def parse_load_value():
    try:
        with open('/proc/loadavg') as inp:
            data = inp.read().splitlines()[0]
            return data.split(' ')[0]
    except IOError:
        pass
    return 'NA'


def thread_parser(data, num_tasks):
    for _ in range(num_tasks):
        dom = fromstring(data)
        assert 'reddit' in dom.xpath('//title')[0].text
    print('.', end='')


def download_file(url, path):
    if not os.path.exists(path):
        print('Downloading %s to %s' % (url, path))
        with open(path, 'wb') as out:
            out.write(urlopen(url).read())


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '-n', '--tasks-number', type=int, default=NUM_DOCUMENTS
    )
    opts = parser.parse_args()
    total_num_cpu = cpu_count()
    download_file(
        'https://raw.githubusercontent.com'
        '/lorien/lxmlbench/master/data/reddit.html',
        '.reddit.html'
    )
    with open('.reddit.html') as inp:
        data = inp.read()

    load_val = parse_load_value()
    model_name = parse_cpu_info('model name')
    cache_size = parse_cpu_info('cache size')
    print('### %s' % model_name)

    print('CPU cores: %d  ' % total_num_cpu)
    print('CPU cache: %s  ' % cache_size)
    print('Current system load: %s  ' % load_val)
    print('Documents: %d  ' % opts.tasks_number)
    num_cpu_used = set()
    for div in (None, 0.25, 0.5, 0.75, 1, 1.2):
        if div is None:
            num_cpu = 1
        else:
            num_cpu = round(total_num_cpu * div)
        if num_cpu not in num_cpu_used:
            num_cpu_used.add(num_cpu)
            print('[%d proc]' % num_cpu, end=' ')
            started = time.time()
            pool = []

            per_proc, rest = divmod(opts.tasks_number, num_cpu)
            proc_num_tasks = [per_proc for x in range(num_cpu)]
            for x in range(rest):
                proc_num_tasks[x] += 1

            for pnum in range(num_cpu):
                proc = Process(
                    target=thread_parser,
                    args=[data, proc_num_tasks[pnum]]
                )
                proc.start()
                pool.append(proc)
            [x.join() for x in pool]
            elapsed = time.time() - started
            print(' %.2f sec  ' % elapsed)

if __name__ == '__main__':
    main()
