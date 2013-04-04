#!/usr/bin/python3

from grammar import Grammar
import rules.generated as NewRules

# Script for generating the parse table used by the parser.

def main():
        grammar = Grammar(NewRules.RULES, NewRules.START_SYMBOL)

    # See https://www.student.cs.uwaterloo.ca/~cs444/jlalr/cfg.html for format
    terminals = grammar.terminals()
    nonterminals = grammar.nonterminals()
    start_symbol = grammar.start_symbol

    print(len(terminals))
    for terminal in terminals:
        print(terminal)

    print(len(nonterminals))
    for nonterm in nonterminals:
        print(nonterm)

    print(start_symbol)

    print(sum([len(grammar.rules[nonterm])
                    for nonterm in grammar.rules]))

    for nonterm in nonterminals:
        for rule in grammar.rules[nonterm]:
            print("%s %s" % (nonterm, ' '.join(rule)))

if __name__ == '__main__':
    main()

