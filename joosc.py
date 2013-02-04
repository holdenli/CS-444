#!/usr/bin/python3

import sys
import optparse
import pprint

import scanner

def parse_options(args=sys.argv):
    parser = optparse.OptionParser()
    parser.add_option('-p', '--print-tokens', action='store_true', default=False,
        help="Print tokens generated by the scanner")

    return parser.parse_args()

def main():
    (opts, args) = parse_options()
    
    if len(args) != 1:
        print("Invalid number of arguments.")
        sys.exit(2)
 
    with open(args[0], 'r') as f:
        tokens = scanner.scan(f.read())
        if opts.print_tokens:
            pprint.pprint(tokens)

if __name__ == "__main__":
    try:
        main()
        
        print("compiled successfully", file=sys.stderr)
    except SystemExit as e:
        print("exited with %d" % e.code, file=sys.stderr)
        sys.exit(e.code)

