#!/usr/bin/python3

import os
import sys
import re

# StdoutCapture
# Used to suppress stdout and save it for future use
#
class StdoutCapture:

    saved = None
    capture = ""

    def __init__(self):
        self.saved = sys.stdout

    def write(self, msg):
        #self.saved.write(msg)
        self.capture += msg

# TestRunner
# This class runs a given function on a batch of test inputs
#
# See scanner.py for an example
#
class TestRunner:

    _name = "Unknown"
    _foo = None
    
    assignment = "a1"
    re_type = "JOOSW:|JOOS2:"
    re_expected = "_EXCEPTION"
    
    verbose = False

    def __init__(self, name, func):
        self._name = name
        self._foo = func

    # Test given against expected value based on file
    # Note:
    #   The verification currently is regex matching of header comments
    #   which are assumed to be within the first 5 lines
    def test(self, value, path):
        with open(path, 'r') as f:
            for i in range(1,6):
                line = f.readline()
                if re.search(self.re_type, line):
                    if re.search(self.re_expected, line):
                        return value != 0
                    break
        return value == 0

    # Run test batch
    def run(self):
        tests_path = "assignment_testcases/{}".format(self.assignment)
        test_total = 0
        test_fails = 0

        print("Running test suite: '{}'".format(self._name))
        print("==================================================")

        sys.stdout = StdoutCapture()

        # Loop through test cases (files)
        for root, subFolders, files in os.walk(tests_path):
            for f in files:
                test_path = os.path.join(root, f)
                if test_path[-5:] != ".java":
                    continue
                test_total += 1
                ret = self._foo(test_path)
                if self.test(ret, test_path) == False:
                    test_fails += 1
                    sys.stdout.saved.write("# TEST FAIL: {}\n".format(f))
                    if self.verbose == True:
                        sys.stdout.saved.write("= OUTPUT: ========================================\n")
                        sys.stdout.saved.write(sys.stdout.capture)
                        sys.stdout.saved.write("==================================================\n")
                sys.stdout.capture = ""

        # Done tests
        sys.stdout = sys.stdout.saved
        print("Test run successful.")
        print("{} test(s) ran. {} test(s) failed.".format(test_total, test_fails))

if __name__ == "__main__":
    def f(a):
        print(a)

    ts = TestRunner("FACK", f)
    ts.run()

