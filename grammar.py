# List of CFG rules for Joos.
# There are two grammars presented in the specification. The first grammar
# presented broken down between the sections of the specifications, and the
# second is found in chapter 18. They are semantically-equivalent; the former
# was used.
#
# Representation:
# Each rule is represented by a key-value-pair [A: B], where A is a
# non-terminal and B is a (possibly empty) list of lists. Each sublist
# is an expansion (i.e., production rule) for A.

import scanner

class Grammar:
    def __init__(self, rules, start_symbol):
        self.rules = rules
        self.start_symbol = start_symbol

    def symbols(self):
        return self.terminals() | self.nonterminals()

    def terminals(self):
        terminals = set()
        terminals.update(scanner.MULTILINE_PATTERNS.keys())
        terminals.update(scanner.SINGLELINE_PATTERNS.keys())
        terminals.update(scanner.STRINGS.values())
        terminals.update(scanner.AUGMENTS)
        return terminals

    def nonterminals(self):
        return set(self.rules.keys())

