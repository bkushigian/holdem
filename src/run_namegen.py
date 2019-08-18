#!/usr/bin/python3

from sys import argv, exit
from remote.namegen import NameGenerator

if len(argv) == 1:
    n = 1
elif len(argv) == 2:
    try:
        n = int(argv[1])
    except RuntimeError:
        print("couldn't parse int", argv[1])
        exit(1)
else:
    print("usage: run_namegen.py [n]\n    generate n names (default 1)")
    exit(1)

ng = NameGenerator()
for i in range(n):
    print(ng.generate_username())
