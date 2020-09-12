# CPU Speed Benchmark

This is simple benchmark which uses lxml library to parse HTML. It performs multiple iterations using 1 CPU core, 2 CPU cores, up to all available CPU cores. On each iteration it parses 1000 documents. On 2Ghz processor it takes about 40-60 seconds to process these number of documents on 1 core. You can change number of documents with `-n` option.

Check wiki to see results of tests on different machines: https://github.com/lorien/lxmlbench/wiki/Test-Results


## How to run test

You need python3 and lxml library. You can install lxml library with command: `python3 -m pip install --user lxml`

Command to run test: `pyton3 runtest.py`

On new machine you can use this one-liner to download and run test:
```
curl -s https://raw.githubusercontent.com/lorien/lxmlbench/master/runtest.py | python3 -
```

You might need to install lxml. Use `pip3 install lxml`. If you do not have pip installed then on Debian/Ubuntu use `sudo apt install python3-lxml`.


## Selectolax parser

By default lxml library is used to parse HTML. You can use [selectolax](https://github.com/rushter/selectolax) parser by providing `-e selectolax` option.

To install selectolax library use command `python3 -m pip install --user selectolax`


## Usage

```
usage: runtest.py [-h] [-n TASKS_NUMBER] [-e ENGINE]

optional arguments:
  -h, --help            show this help message and exit
  -n TASKS_NUMBER, --tasks-number TASKS_NUMBER
                        Number of documents to parse. Default is 1000
  -e ENGINE, --engine ENGINE
                        Parsing engine, use comma to specify multiple values.
                        Available engines: lxml, selectolax. Default is lxml.
```


## Support

Telegram chat: [@grablab](https://t.me/grablab)
