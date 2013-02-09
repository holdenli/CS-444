#!/usr/bin/python3

import sys
from pprint import pprint

# ParseTable
# The assumption is that the grammar and parse table here is
# LR1 with no reduce-reduce or reduce-shift conflicts
class ParseTable:
    terminals = []
    nonterminals = []
    start = None
    productions = [] # ( nonterm, productions )
    lr1_states = None
    lr1_t = [] # ( state, term/symbol, reduce?, rule/state )

    # Really only to be used with read_parse_table
    def __init__(self, cfg, lr1):
        self.terminals = cfg[0]
        self.nonterminals = cfg[1]
        self.start = cfg[2]
        for p in cfg[3]:
            pp = p.split()
            self.productions.append((pp[0], pp[1:]))

        self.lr1_states = lr1[0]
        for t in lr1[1]:
            tt = t.split()
            self.lr1_t.append((
                    int(tt[0])
                    , tt[1]
                    , tt[2] == "reduce"
                    , int(tt[3])
                ))
        pprint(self.lr1_t)

    # False if no next state (could be reduce)
    def next_state(self, state, symbol, reduce):
        for t in self.lr1_t:
            if t[0] == state and t[1] == symbol and t[2] == reduce:
                return t[3]
        return False

# read_parse_table
# This is some ugly code to return generate tuples used to generate the ParseTable
def read_parse_table(parse_table):
    with open(parse_table, 'r') as f:
        lines = f.read().splitlines()
        
        # CFG
        t = int(lines[0])
        n = int(lines[t+1])
        S = lines[t+n+2].strip()
        r = int(lines[t+n+3])
        lr1_statestart = t + n + r + 3 + 1
        cfg = lines[0:lr1_statestart]
        
        # LR1
        lr1_ = lines[lr1_statestart:]
        lr1_states = int(lr1_[0])
        lr1_t = int(lr1_[1])
        if lr1_t != len(lr1_[2:]):
            print("ERROR: Invalid LR1", file=sys.stderr)
            sys.exit(42)

        return ParseTable(
                (cfg[1:1+t], cfg[t+2:t+2+n],  S, cfg[t+n+4:t+n+4+r])
                , (lr1_states, lr1_[2:])
            )
    pass

# reduce
# Returns the production rule or False if it can't be found
def reduce(parse_table, stack, a):
    # traverse DFA
    state = 0
    for symbol in stack:
        state = parse_table.next_state(state, symbol, False)
        if state == False:
            return False

    rule = parse_table.next_state(state, a, True)
    
    if rule == False:
        return False
    
    rule = parse_table.productions[rule]
    return rule
    #print("ERROR: Reduce failed with stack: {}".format(stack))

# reject
# True if stack is not a viable prefix and False otherwise
def reject(parse_table, stack):
    state = 0
    for symbol in stack:
        state = parse_table.next_state(state, symbol, False)
        if state == False:
            return True
    
    return False

# parse
# takes list of tokens, returns parse tree or false
#
# Dev Notes:
#   Currently only returns true or false
#   Need to do pop properly
#   Input must be list of strings instead of list of token tuples
#       This can be fixed but it's kinda messy...
#   So the two options are:
#       - fill in the parse tree with matching tokens in parallel
#       - change it to handle tokens and fill in the tree naturally
def parse(input, parse_table):
    print("PARSE:")
    print(input)

    tree = None
    stack = []
    for a in input:
        print("PARSE LOOP:")
        print(a)
        print(stack)
        while reduce(parse_table, stack, a) != False:
            production = reduce(parse_table, stack, a)
            stack.pop() # TODO pop everything in rule
            stack.append(production[0])
            print("REDUCE!")
            print(stack)
        print("REJECT?")
        print(stack + [a])
        if reject(parse_table, stack + [a]):
            "REJECTED!"
            return False
        stack.append(a)
    return True

if __name__ == "__main__":
    import scanner
    t = scanner.scan("assignment_testcases/others/sample.java")
    t = [("BOF", "BOF"), ("id", "fat"), ("EOF", "EOF")]
    t = ["BOF", "id", "EOF"]
    z = read_parse_table("assignment_testcases/others/sample.lr1")
    print(parse(t, z))

