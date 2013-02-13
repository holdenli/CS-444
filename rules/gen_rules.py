#!/usr/bin/python3

import pprint
import sys

terms = []
nonterm = ""

g = {}

for line in sys.stdin:
    line = line.strip()

    if line == '':
        continue

    if line[-1] == ':':
        nonterm = line[:-1].strip()
        g[nonterm] = []
    else:
        if line == '__EPSILON__':
            g[nonterm].append([])
        else:
            g[nonterm].append(line.split())

print('START_SYMBOL="Goal"')
print('RULES = %s' % pprint.pformat(g, width=20))
