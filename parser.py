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
    # Really only to be used with read_parse_table
    def __init__(self, cfg, lr1):
        # CFG
        self.terminals = cfg[0]
        self.nonterminals = cfg[1]
        self.start = cfg[2]
        self.productions = [] # ( nonterm, productions )
        for p in cfg[3]:
            pp = p.split()
            self.productions.append((pp[0], pp[1:]))

        # LR1
        self.lr1_states = lr1[0]
        self.lr1_d = {}
        for t in lr1[1]:
            tt = t.split()
            self.lr1_d['%s %s %s' % (tt[0], tt[1], tt[2] == 'reduce')] = int(tt[3])
        
        logging.debug("ParseTable LR(1) Transitions:\n%s\n%s\n%s"
            % ("*"*20, pprint.pformat(self.lr1_d), "*"*20))

    # False if no next state (could be reduce)
    def next_state(self, state, symbol, reduce):
        try:
            return self.lr1_d['%s %s %s' % (state, symbol, reduce)] 
        except KeyError:
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
    logging.info("PARSE: %s" % (pprint.pformat(tokens)))

    tree = None
    stack = []
    node_stack = [] # keep nodes in a parallel stack cause its easier suck it
    for a in tokens:
        logging.info(">>PARSE LOOP")
        logging.info("  " + str(a))
        logging.info("  " + str(stack))
        
        # Reduce
        production = parse_reduce(parse_table, stack, a)
        while production != False:
            children = []
            # Remove RHS from stack
            for p in reversed(production[1]):
                if stack.pop()[0] != p:
                    logging.error("PARSE ERROR: Stack did not match production ('%s')" % (p))
                    sys.exit(1)
                children.insert(0, node_stack.pop())
            stack.append((production[0], None))
            node_stack.append(node.Node(production[0], None, children))
            logging.info("#PARSE REDUCE : %s" % (stack))

            production = parse_reduce(parse_table, stack, a)
        
        # Reject?
        if parse_reject(parse_table, stack + [a]):
            logging.info("#FAIL         : %s" % (stack + [a]))
            return False
        
        # Shift
        stack.append(a)
        node_stack.append(node.Node(a[0], a, []))
        
        logging.info("#PARSE SHIFT  : %s" % (stack))
        logging.info("#NODE STACK   : %s" % (node_stack))
    
    # Accept
    return node.Node("ROOT", children=node_stack)

if __name__ == "__main__":
    import scanner
    
    logging.setLogLevel("INFO")

    t = [("BOF", "BOF"), ("id", "fat"), ("EOF", "EOF")]
    z = read_parse_table("assignment_testcases/others/sample.lr1")
    
    parse_tree = parse(t, z)
    print(parse_tree)
    print("BFS List of all nodes:")
    pprint.pprint(list(parse_tree.bfs_iter()))
    print("List of all leafs:")
    pprint.pprint(parse_tree.leafs())
    
    z = read_parse_table("grammar.lr1")
    with open("assignment_testcases/others/sample.java", 'r') as f:
       t = scanner.scan(f.read())
    parse_tree = parse(t, z)
    print(parse_tree)
    print("BFS List of all nodes:")
    pprint.pprint(list(parse_tree.bfs_iter()))
    print("List of all leafs:")
    pprint.pprint(parse_tree.leafs())

