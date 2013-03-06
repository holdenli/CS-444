#!/usr/bin/python3

import os
import sys

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
    _work_func = None # func(test_path)
    _test_func = None # func(test_value, test_name)
    
    test_folder = "assignment_testcases"
    test_subfolder = "a1"
    
    verbose = False
    def __init__(self, name, work, test):
        self._name = name
        self._work_func = work
        self._test_func = test

    # Run test batch
    def run(self):
        tests_path = "%s/%s" % (self.test_folder, self.test_subfolder)
        test_total = 0
        test_fails = 0

        print("Running test suite: '%s'" % self._name)
        print("==================================================")

        newout = OutputCapture()
        sys.stdout = newout
        #sys.stderr = newout
        
        # Loop through test cases (files)
        for test_name in os.listdir(tests_path):
            print(test_name)
            if not test_name.startswith("J"):
                continue
            test_path = os.path.join(tests_path, test_name)
            test_total += 1
            ret = self._work_func(test_path)
            if self._test_func(ret, test_name) == False:
                test_fails += 1
                newout.stdwrite("# TEST FAIL %d: %s\n" % (test_fails, test_name))
                if self.verbose == True:
                    newout.stdwrite(sys.stdout.capture)
                    newout.stdwrite("==================================================\n")
            newout.capture = ""

        # Done tests
        sys.stdout = newout.stdout
        sys.stderr = newout.stderr
        print("Test run successful.")
        print("{} test(s) ran. {} test(s) failed.".format(test_total, test_fails))

# Primary Test Functions
##########################
import joosc

def test_work(path):
    try:
        if path.endswith(".java"):
            joosc.joosc([path], "end")
        elif os.path.isdir(path):
            paths = []
            for (path, dirs, files) in os.walk(path):
                paths.extend([os.path.join(path, f) for f in files])
            joosc.joosc(paths, "end")
        else:
            return 1
        return 0
    except SystemExit as e:
        return 1

# This is given the return value of the function run and the test name and
# determines if the return value is valid
def test_test(value, name):
    import re
    if re.search("^Je", name): 
        return value != 0
    else:
        return value == 0

def test_joosc(test_name, verbose):
    ts = TestRunner("JOOSC", test_work, test_test)
    ts.test_subfolder = test_name
    ts.verbose = verbose
    ts.run()

