# CPU Speed Benchmark

This is simple benchmark which uses lxml library to parse HTML. It performs multiple iterations using 1 CPU core, 2 CPU cores, up to all available CPU cores. On each iteration it parses 1000 documents. On 2Ghz processor it takes about 40-60 seconds to process these numbers of documents on 1 core. You can change number of documents with `-n` option.

Check wiki to see results of test on different machines: https://github.com/lorien/lxmlbench/wiki/Test-Results

## Installation

You need python3 and lxml library. You can install lxml library with command: `python3 -m pip install --user lxml`

## How to run test

Just run command `pyton3 runtest.py`

## One-liner

`curl -s https://raw.githubusercontent.com/lorien/lxmlbench/master/runtest.py | python3 -`

Do not be afraid to run this command. There is no `rm -rf /` inside. Yet.
