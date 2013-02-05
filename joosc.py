#!/usr/bin/python3

import sys
import optparse
import pprint

import test
import scanner

def parse_options(args=sys.argv):
    parser = optparse.OptionParser()
    parser.add_option('-d', '--debug', action='store_true', default=False,
        help="Print debug output")
    parser.add_option('-t', '--test', action='store_true', default=False,
        help="Run tests")

    return parser.parse_args()

def joosc(program, debug):
    tokens = scanner.scan(program)
    if debug:
        pprint.pprint(tokens)

def test_work(path):
    try:
        with open(path, 'r') as f:
            joosc(f.read(), False)
        return 0
    except SystemExit as e:
        return 1

def main():
    (opts, args) = parse_options()
    
    if opts.test:
        print("TESTING")
        ts = test.TestRunner("JOOSC", test_work)
        ts.assignment = "a1"
        ts.re_expected = "_EXCEPTION"
        ts.verbose = opts.debug
        ts.run()
        return 0
 
    if len(args) != 1:
        print("Invalid number of arguments.")
        sys.exit(2)

    with open(args[0], 'r') as f:
        joosc(f.read(), opts.debug)

if __name__ == "__main__":
    try:
        main()
        print("compiled successfully", file=sys.stderr)
    except SystemExit as e:
        print("exited with %d" % e.code, file=sys.stderr)
        sys.exit(e.code)

