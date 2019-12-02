#!/usr/bin/env python3
"""
Most of calls of print function in this code
use double space at end of output string. It is to force
markdown parser to enter new line, in case you want to put
output of test into markdown document.

See results of tests runned on different machines here:
https://github.com/lorien/lxmlbench/wiki/Test-Results
"""
import sys
from argparse import ArgumentParser
import time
from multiprocessing import cpu_count, Process
from urllib.request import urlopen
import os

NUM_DOCUMENTS = 1000
ENGINES = ('lxml', 'selectolax')


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


def thread_parser_lxml(data, num_tasks):
    from lxml.html import fromstring

    for _ in range(num_tasks):
        dom = fromstring(data)
        assert 'reddit' in dom.xpath('//title')[0].text
    print('.', end='')


def thread_parser_selectolax(data, num_tasks):
    from selectolax.parser import HTMLParser

    for _ in range(num_tasks):
        dom = HTMLParser(data)
        assert 'reddit' in dom.css('title')[0].text()
    print('.', end='')


def download_file(url, path):
    if not os.path.exists(path):
        print('Downloading %s to %s' % (url, path))
        with open(path, 'wb') as out:
            out.write(urlopen(url).read())


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '-n', '--tasks-number', type=int, default=NUM_DOCUMENTS,
        help=(
            'Number of documents to parse.'
            ' Default is %d' % NUM_DOCUMENTS
        ),
    )
    parser.add_argument(
        '-e', '--engine',
        default='lxml',
        help=(
            'Parsing engine, use comma to specify multiple values.'
            ' Available engines: lxml, selectolax.'
            ' Default is lxml.'
        ),
    )
    opts = parser.parse_args()
    total_num_cpu = cpu_count()

    engines = opts.engine.split(',')
    for engine in engines:
        if engine not in ENGINES:
            sys.stderr.write(
                'Invalid value for --engine option: %s\n' % engine
            )
            sys.exit(1)

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
    engine_func_reg = {
        'lxml': thread_parser_lxml,
        'selectolax': thread_parser_selectolax,
    }

    for engine_idx, engine in enumerate(engines):
        if engine_idx:
            # Display new line between different engine outputs
            print('')
        print('### %s' % model_name)
        print('CPU cores: %d  ' % total_num_cpu)
        print('CPU cache: %s  ' % cache_size)
        print('System load before test: %s  ' % load_val)
        print('Documents: %d  ' % opts.tasks_number)
        print('Engine: %s  ' % engine)

        num_cpu_used = set()
        for div in (None, 0.25, 0.5, 0.75, 1, 1.2):
            if div is None:
                num_cpu = 1
            else:
                num_cpu = max(1, round(total_num_cpu * div))
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
                        target=engine_func_reg[engine],
                        args=[data, proc_num_tasks[pnum]]
                    )
                    proc.start()
                    pool.append(proc)
                [x.join() for x in pool]
                elapsed = time.time() - started
                print(' %.2f sec  ' % elapsed)

if __name__ == '__main__':
    main()
