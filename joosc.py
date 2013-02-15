#!/usr/bin/python3

import sys
import optparse
import pprint
from utils import logging

import test
import scanner
import parser
import weeder

parse_table = parser.read_parse_table('grammar.lr1')

def parse_options(args=sys.argv):
    parser = optparse.OptionParser()
    parser.add_option('-l', '--loglevel', action='store', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help="""Logging level. Choices: DEBUG, INFO, WARNING, ERROR.
            [default: INFO]""")

    parser.add_option('-t', '--test', action='store', dest='test',
        help="Run tests")

    return parser.parse_args()

def joosc(program):
    global parse_table

    tokens = scanner.scan(program)
    logging.debug("Tokens returned from scanner:\n", pprint.pformat(tokens))

    parse_tree = parser.parse(tokens, parse_table)
    if parse_tree == False:
        logging.error("Could not parse")
        sys.exit(42)

    weeder.weed(parse_tree);

def test_work(path):
    try:
        with open(path, 'r') as f:
            joosc(f.read())
        return 0
    except SystemExit as e:
        return 1

def main(argv=sys.argv):
    (opts, args) = parse_options(argv)

    logging.setLogLevel(level=opts.loglevel)
    
    if opts.test:
        logging.info("TESTING")
        ts = test.TestRunner("JOOSC", test_work)
        ts.assignment = opts.test
        ts.re_expected = "_EXCEPTION"
        ts.verbose = (opts.loglevel == 'DEBUG')
        ts.run()
        return 0
 
    if len(args) != 1:
        logging.error("Invalid number of arguments.")
        sys.exit(2)

    with open(args[0], 'r') as f:
        joosc(f.read())

if __name__ == "__main__":
    try:
        main()
        logging.info("compiled successfully")
    except SystemExit as e:
        logging.info("exited with %d" % e.code)
        sys.exit(e.code)

