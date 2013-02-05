#!/usr/bin/python3

import sys

def read_parse_table(parse_table):
    import pprint
    with open(parse_table, 'r') as f:
        lines = f.readlines()
        t = int(lines[0])
        n = int(lines[t+1])
        S = lines[t+n+2].strip()
        r = int(lines[t+n+3])
        lr_start = t + n + r + 3 + 1
        cfg = lines[0:lr_start]
        print("CFG:")
        pprint.pprint(cfg)
        pprint.pprint(lines[lr_start:])
    pass

if __name__ == "__main__":
    read_parse_table("sample.lr1")

