#!/usr/bin/python3

import sys
from utils import node
from utils import logging
import pprint

# ParseTable
# The assumption is that the grammar and parse table here is
# LR1 with no reduce-reduce or reduce-shift conflicts
# ie. there is little error checking here...
#
# Impl Notes:
# - ParseTable uses symbol names throughout but
#   all parse functions hold symbols in a tuple where
#   the first element is the symbol name.
# - If the second element is None then then it is a nonterminal
#   otherwise it is a terminal (a token with line number)
#
# WARNING:
#   MAN, the parse table code is disgusting. Just let Holden deal with it.
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
        
        logging.debug("ParseTable LR(1) Transitions:\n%s\n%s\n%s"
            % ("*"*20, pprint.pformat(self.lr1_t), "*"*20))

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
            logging.error("PARSE ERROR: Invalid LR1")
            sys.exit(1)

        return ParseTable(
                (cfg[1:1+t], cfg[t+2:t+2+n],  S, cfg[t+n+4:t+n+4+r])
                , (lr1_states, lr1_[2:])
            )
    pass

# reduce
# Returns the production rule or False if it can't be found
def parse_reduce(parse_table, stack, a):
    # traverse DFA using stack as input
    state = 0
    for symbol in stack:
        state = parse_table.next_state(state, symbol[0], False)
        if state == False:
            return False

    # get rule
    rule = parse_table.next_state(state, a[0], True)
    if rule == False:
        return False
    
    rule = parse_table.productions[rule]
    return rule

# reject
# True if stack is not a viable prefix and False otherwise
def parse_reject(parse_table, stack):
    state = 0
    for symbol in stack:
        state = parse_table.next_state(state, symbol[0], False)
        if state == False:
            return True
    return False

# parse
# takes list of tokens, returns parse tree or false
#
# Notes:
# - Should it error 42 instead of false?
def parse(tokens, parse_table):
    logging.debug("PARSE: %s" % (pprint.pformat(tokens)))

    tree = None
    stack = []
    node_stack = [] # keep nodes in a parallel stack cause its easier suck it
    for a in tokens:
        logging.debug(">>PARSE LOOP")
        logging.debug("  " + str(a))
        logging.debug("  " + str(stack))
        
        # Reduce
        while parse_reduce(parse_table, stack, a) != False:
            production = parse_reduce(parse_table, stack, a)
            children = []
            for p in production[1]:
                if stack.pop()[0] != p:
                    logging.error("PARSE ERROR: Stack did not match production")
                    sys.exit(1)
                children += [node_stack.pop()]
            stack.append((production[0], None))
            node_stack.append(node.Node(production[0], None, children))
            logging.debug("#PARSE REDUCE : %s" % (stack))
        
        # Reject?
        if parse_reject(parse_table, stack + [a]):
            return False
        
        # Shift
        stack.append(a)
        node_stack.append(node.Node(a[0], a, []))
        
        logging.debug("#PARSE SHIFT  : %s" % (stack + [a]))
        logging.debug("#NODE STACK   : %s" % (node_stack))
    
    # Accept
    return node.Node("ROOT", c=node_stack)

if __name__ == "__main__":
    import scanner
    
    logging.setLogLevel("DEBUG")
    
    t = scanner.scan("assignment_testcases/others/sample.java")
    t = [("BOF", "BOF"), ("id", "fat"), ("EOF", "EOF")]
    z = read_parse_table("assignment_testcases/others/sample.lr1")

    parse_tree = parse(t, z)
    print(parse_tree)
    print("BFS List of all nodes:")
    pprint.pprint(list(parse_tree.bfs_iter()))
    print("List of all leafs:")
    pprint.pprint(parse_tree.leafs())

