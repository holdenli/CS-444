#!/usr/bin/python3

import sys
import optparse
import pprint
from utils import logging

import test
import scanner
import parser
import weeder
import ast
from utils import class_hierarchy

from environment import build_environments
import typelink

# Globals
##########################

parse_table = parser.read_parse_table('grammar.lr1')

# COMPILING
##########################

# Parses a program and returns its AST
def get_ast(program, filename, stage='end'):
    global parse_table
    tokens = scanner.scan(program)
    logging.debug("Tokens returned from scanner:\n", pprint.pformat(tokens))
    if stage == 'scanner':
        sys.exit(0)

    parse_tree = parser.parse(tokens, parse_table)
    if parse_tree == False:
        logging.error("Could not parse")
        sys.exit(42)
    if stage == 'parser':
        parse_tree.pprint()
        sys.exit(0)

    weeder.weed(parse_tree, filename)
    if stage == 'weeder':
        parse_tree.pprint()
        sys.exit(0)

    abstract_syntax_tree = ast.build_ast(parse_tree)
    if stage == 'ast':
        abstract_syntax_tree.pprint()
        sys.exit(0)

    return abstract_syntax_tree

# Main work
def joosc(files, stage):
    ast_list = []
    for i in files:
        with open(i, 'r') as f:
            ast_list.append(get_ast(f.read(), i, stage))
   
    pkg_index = build_environments(ast_list)
    
    typelink.typelink(ast_list, pkg_index)

    class_hierarchy.class_hierarchy(ast_list, None)


# INTERFACE
##########################

def parse_options(args=sys.argv):
    parser = optparse.OptionParser()
    parser.add_option('-l', '--loglevel', action='store', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help="""Logging level. Choices: DEBUG, INFO, WARNING, ERROR.
            [default: WARNING]""")

    parser.add_option('-t', '--test', action='store', dest='test',
        help="Run tests")

    parser.add_option('-s', '--stage', action='store', dest='stage',
        default='end', choices=['scanner', 'parser', 'weeder', 'ast', 'end'],
        help="Stage of compiler to run \"up to\".")

    parser.add_option('-i', '--include_stdlib', action='store_true',
        dest='include_stdlib')

    return parser.parse_args()

def main(argv=sys.argv):
    (opts, args) = parse_options(argv)

    logging.setLogLevel(level=opts.loglevel)
    
    if opts.test:
        logging.info("TESTING %s" % (opts.test))
        test.test_joosc(opts.test, opts.loglevel == 'WARNING',
            opts.include_stdlib)
        return 0
 
    if len(args) < 1:
        logging.info("Nothing to compile.")
        return 0

    paths = [
        "stdlib/5.0/java/lang/Byte.java",
        "stdlib/5.0/java/lang/Character.java",
        "stdlib/5.0/java/lang/Class.java",
        "stdlib/5.0/java/lang/Cloneable.java",
        "stdlib/5.0/java/lang/Integer.java",
        "stdlib/5.0/java/lang/Number.java",
        "stdlib/5.0/java/lang/Object.java",
        "stdlib/5.0/java/lang/Short.java",
        "stdlib/5.0/java/lang/String.java",
        "stdlib/5.0/java/lang/System.java",
    ]
    if opts.include_stdlib is True:
        args.extend(paths)

    joosc(args, opts.stage)

if __name__ == "__main__":
    try:
        main()
        logging.info("compiled successfully")
    except SystemExit as e:
        logging.info("exited with %d" % e.code)
        sys.exit(e.code)

