#!/usr/bin/python3

import grammar
import scanner

def main():
    
    # see https://www.student.cs.uwaterloo.ca/~cs444/jlalr/cfg.html for format
    terminals = grammar.terminals()
    nonterminals = grammar.nonterminals()
    start_symbol = grammar.START_SYMBOL

    print(len(terminals))
    for terminal in terminals:
        print(terminal)

    print(len(nonterminals))
    for nonterm in nonterminals:
        print(nonterm)

    print(start_symbol)

    print(sum([len(grammar.RULES[nonterm])
                    for nonterm in grammar.RULES]))

    for nonterm in nonterminals:
        for rule in grammar.RULES[nonterm]:
            print("%s %s" % (nonterm, ' '.join(rule)))

if __name__ == '__main__':
    main()
