#!/usr/bin/python3

import os
import sys
import re

# OutputCapture
# Used to suppress stdout and save it for future use
# Warning: This is kinda dangerous because it may hide real errors
#
class OutputCapture:

    def __init__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.capture = ""

    def stdwrite(self, msg):
        self.stdout.write(msg)

    def write(self, msg):
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

    """
    Eh, this is too complex. Forget it.
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
    """

    # This is given the return value of the function run and the test name and
    # determines if the return value is valid
    def test(self, value, name):
        if re.search("^Je", name): 
            return value != 0
        else:
            return value == 0

    # Run test batch
    def run(self):
        tests_path = "assignment_testcases/%s" % self.assignment
        test_total = 0
        test_fails = 0

        print("Running test suite: '%s'" % self._name)
        print("==================================================")

        newout = OutputCapture()
        sys.stdout = newout
        sys.stderr = newout

        # Loop through test cases (files)
        for f in os.listdir(tests_path):
            if not f.endswith(".java"):
                continue
            test_path = os.path.join(tests_path, f)
            test_total += 1
            ret = self._foo(test_path)
            if self.test(ret, f) == False:
                test_fails += 1
                newout.stdwrite("# TEST FAIL %d: %s\n" % (test_fails, f))
                if self.verbose == True:
                    newout.stdwrite(sys.stdout.capture)
                    newout.stdwrite("==================================================\n")
            newout.capture = ""

        # Done tests
        sys.stdout = newout.stdout
        sys.stderr = newout.stderr
        print("Test run successful.")
        print("{} test(s) ran. {} test(s) failed.".format(test_total, test_fails))

if __name__ == "__main__":
    def f(a):
        print(a)

    ts = TestRunner("FACK", f)
    ts.run()

