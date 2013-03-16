#!/usr/bin/python3

import joosc
import logging
import os
import re
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
    
    test_folder = "assignment_testcases"
    test_subfolder = "a1"
    
    verbose = False

    def __init__(self, name, joosc_options):
        self._name = name
        self._joosc_options = joosc_options

    # Run test batch
    def run(self, show_errors):
        tests_path = "%s/%s" % (self.test_folder, self.test_subfolder)
        test_paths = list(os.listdir(tests_path))

        forks = 4
        n = len(test_paths)
        k = int(n/forks)
        parts = []
        for i in range(int(n/k)):
            if i+1 == int(n/k):
                parts.append(test_paths[i*k:])
            else:
                parts.append(test_paths[i*k:(i+1)*k])

        print("Running test suite: '%s' [forks=%s]" % (self._name, forks))
        print("==================================================")

        me = forks
        rdby = forks/2
        chldrn = []
        while me%2 == 0 and me > 0:

            r = os.fork()
            if r == 0:
                # new!
                me = me + rdby
                rdby = rdby/2
            else:
                me = me - rdby
                rdby = rdby/2
                chldrn.append(r)
        
        me = int((int(me) - 1)/2)

        test_total = 0
        test_fails = 0

        newout = OutputCapture()
        sys.stdout = newout
        if show_errors == False: # Hide errors if specified.
            sys.stderr = newout
        
        # Loop through test cases (files)

        for test_name in parts[me]:
            print(test_name)
            if not test_name.startswith("J"):
                continue
            test_path = os.path.join(tests_path, test_name)
            test_total += 1

            # Run joosc (i.e., run the test).
            ret = self.run_joosc(test_path)

            # If we did not obtain the desired result, save it.
            if self.is_correct_result(ret, test_name) == False:
                test_fails += 1
                d = ''
                if forks == 1:
                    d = ' %s' % test_fails

                newout.stdwrite("# TEST FAIL%s: %s\n" % (d, test_name))

                # Capture verbose output (i.e., errors) if necessary.
                if self.verbose == True:
                    newout.stdwrite(sys.stdout.capture)
                    newout.stdwrite("==================================================\n")
            else:
                newout.stdwrite('.')
                newout.stdout.flush()
            newout.capture = ""

        # Done tests
        sys.stdout = newout.stdout
        sys.stderr = newout.stderr
        print("Test run successful.")
        print("{} test(s) ran. {} test(s) failed.".format(test_total, test_fails))

        for c in chldrn:
            try:
                os.waitpid(c, 0)
            except:
                pass

    def run_joosc(self, path):
        try:
            if path.endswith(".java") or os.path.isdir(path):
                # joosc.joosc requires the first argument to be a list.
                joosc.joosc([path], self._joosc_options)
            else:
                return 1
            return 0
        except SystemExit as e:
            return e.code

    # This is given the return value of the function run and the test name and
    # determines if the return value is valid
    def is_correct_result(self, value, name):
        if re.search("^Je", name): 
            return value != 0
        else:
            return value == 0

# Primary Test Functions
##########################

# Initializes test running and executes the testing procedure.
# Called by joosc.py.
def setup_and_run(test_name, show_errors, verbose, joosc_options):
    ts = TestRunner("JOOSC", joosc_options)
    ts.test_subfolder = test_name
    ts.verbose = verbose
    ts.run(show_errors)

