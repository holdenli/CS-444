#!/usr/bin/python3

import joosc
import logging
import os
import re
import sys
import subprocess
import time

from multiprocessing import Pool, Manager

def num_cores():
    """ number of cores available on this machine """
    try:
        return int(subprocess.check_output("nproc").strip())
    except:
        logging.warn("Could not determine the number of cores.  Using 4.")
        return 4

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
        test_total = 0
        test_fails = 0

        print("Running test suite: '%s'" % self._name)
        print("==================================================")

        q = Manager().Queue()
        p_list = []
        
        pool = Pool(processes=num_cores())

        start_time = time.time()
        # Loop through test cases (files)
        for test_name in os.listdir(tests_path):
            if not test_name.startswith("J"):
                continue
            test_path = os.path.join(tests_path, test_name)
            test_total += 1

            # Run joosc (i.e., run the test).
            p = pool.apply_async(func=run_joosc, args=(self._joosc_options, test_path, q, ))
            p_list.append(p)

        for p in p_list:
            ret = q.get(5)
            
            if ret[0] < 0:
                print("#\nUNEXPECTED ERROR: %s" % os.path.split(ret[1])[1])

            elif self.is_correct_result(ret[0], os.path.split(ret[1])[1]) == False:
                test_fails += 1
                print("#\nTEST FAIL %d: %s" % (test_fails, os.path.split(ret[1])[1]))
                if self.verbose:
                    print("OUTPUT:")
                    print("==================================================")
                    print(ret[2])
                    print("==================================================")

            else:
                sys.stdout.write('.')
                sys.stdout.flush()

        # Done tests
        print("\n==================================================")
        print("Test run successful.  %s seconds" % (time.time() - start_time))
        print("{} test(s) ran. {} test(s) failed.".format(test_total, test_fails))

    
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

def run_joosc(joosc_options, path, q):
    capture = OutputCapture()
    sys.stdout = capture
    sys.stderr = capture
    try:
        if path.endswith(".java") or os.path.isdir(path):
            # joosc.joosc requires the first argument to be a list.
            joosc.joosc([path], joosc_options)
        else:
            q.put([1, path, capture.capture])
            return
        q.put([0, path, capture.capture])
        return
    except SystemExit as e:
        if e.code == 42:
            q.put([1, path, capture.capture])
        else:
            q.put([-1, path, ""]) 
    except:
        q.put([-1, path, ""]) 

if __name__ == "__main__":
    import shutil
    shutil.copyfile('lib/stdlib/5.1/runtime.s', 'output/runtime.s')

    from subprocess import call
    ret = call("rm output/*.o", shell=True)

    for name in os.listdir("output"):
        path = os.path.join("output", name)
        print(path)
        ret = call("/u/cs444/bin/nasm -O1 -f elf -g -F dwarf %s" % (path), shell=True)
        if ret != 0:
            logging.warning("nasm on %s failed" % (path))
            sys.exit(1)
    
    ret = call("ld -melf_i386 -o main output/*.o", shell=True)
    if ret != 0:
        logging.warning("ld on failed")
        sys.exit(1)

