# CPU Speed Benchmark

This is simple benchmark which uses lxml library to parse HTML. It performs multiple iterations using 1 CPU core, 2 CPU cores, up to all available CPU cores. On each iteration it parses 300 documents. Defalt number of documents is quite small to finish test on single CPU core in short time. You can change number of documents with `-n` option.

## Installation

You need python3 and lxml library. You can install lxml library with command: `python3 -m pip install --user lxml`

## How to run test

Just run command `pyton3 runtest.py`

## One-liner

`curl -s https://raw.githubusercontent.com/lorien/lxmlbench/master/runtest.py | python3 -`

Do not be afraid to run this command. There is no `rm -rf /` inside. Yet.
