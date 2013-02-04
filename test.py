#!/usr/bin/python3

import os
import sys
import optparse
import pprint

import scanner

# TestRunner
# This class runs a given function on a batch of test inputs
#
# TODO:
#   - Capture failures from function
#   - Provide asserts/verify/etc?
#   - Suppress output; save until error
#   - sys.stdout = open(os.devnull, 'w')
#
# See scanner.py for an example
class TestRunner:

    _name = "Unknown"
    _foo = None
    assignment = 1

    def __init__(self, name, func):
        self._name = name
        self._foo = func

    def run(self):
        test_path = "assignment_testcases/a{}".format(self.assignment)

        print("Running test suite: '{}'".format(self._name))

        # Todo
        for root, subFolders, files in os.walk(test_path):
            print("#Folders: {}".format(subFolders))
            #print(files)
            for f in files:
                print("#File: {}".format(f))
                self._foo(os.path.join(root, f))

def f(a):
    print(a)

if __name__ == "__main__":
    ts = TestSuite("FACK", f)
    ts.run()

