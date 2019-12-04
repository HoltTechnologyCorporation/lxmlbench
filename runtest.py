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
from multiprocessing import cpu_count, Process, Value
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


def thread_parser_lxml(parse_func, data, num_docs):
    while True:
        with num_docs.get_lock():
            if num_docs.value == 0:
                break
            num_docs.value -= 1
            val = num_docs.value
        dom = parse_func(data)
        assert 'reddit' in dom.xpath('//title')[0].text
    print('.', end='')


def thread_parser_selectolax(parse_func, data, num_docs):
    while True:
        with num_docs.get_lock():
            if num_docs.value == 0:
                break
            num_docs.value -= 1
            val = num_docs.value
        dom = parse_func(data)
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
    parser.add_argument(
        '-w', '--workers',
        type=int,
        help=(
            'Run test once, only for specified number of workers.'
        ),
    )
    opts = parser.parse_args()
    total_num_cpu = cpu_count()

    engine_func_reg = {
        'lxml': {
            'thread_func': thread_parser_lxml,
            'parser_func': None,
        },
        'selectolax': {
            'thread_func': thread_parser_selectolax,
            'parser_func': None,
        },
    }
    engines = opts.engine.split(',')
    for engine in engines:
        if engine not in ENGINES:
            sys.stderr.write(
                'Invalid value for --engine option: %s\n' % engine
            )
            sys.exit(1)
        elif engine == 'lxml':
            from lxml.html import fromstring
            engine_func_reg[engine]['parser_func'] = fromstring
        elif engine == 'selectolax':
            from selectolax.parser import HTMLParser
            engine_func_reg[engine]['parser_func'] = HTMLParser

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

        num_docs = Value('l') # l -> signed long, 4 bytes

        stages = []
        if opts.workers:
            stages.append(opts.workers)
        else:
            stages.append(1)
            for mult in (0.25, 0.5, 0.75, 1, 1.2):
                num = max(1, round(total_num_cpu * mult))
                if num not in stages:
                    stages.append(num)

        for num_proc in stages:
            started = time.time()
            num_docs.value = opts.tasks_number
            print('[%d proc]' % num_proc, end=' ')
            pool = []

            for _ in range(num_proc):
                proc = Process(
                    target=engine_func_reg[engine]['thread_func'],
                    args=[
                        engine_func_reg[engine]['parser_func'],
                        data,
                        num_docs
                    ]
                )
                proc.start()
                pool.append(proc)
            [x.join() for x in pool]
            elapsed = time.time() - started
            print(' %.2f sec  ' % elapsed)

if __name__ == '__main__':
    main()
