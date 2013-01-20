#!/usr/bin/python3

import sys
import argparse

import scanner

def parse_options(args=sys.argv):
    parser = argparse.ArgumentParser(description='Compile a Joos source file')
    parser.add_argument('file', help='Joos file to compile')
    
    return parser.parse_args()

def main():
    args = parse_options()
    
    with open(args.file, 'r') as f:
        tokens = scanner.scan(f.read())

if __name__ == "__main__":
    try:
        main()
        
        print("compiled successfully", file=sys.stderr)
    except SystemExit as e:
        print("exited with %s" % e, file=sys.stderr)