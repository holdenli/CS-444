#!/usr/bin/python3

#import inspect
import sys
import os.path

LEVELS = {
    'DEBUG': 1,
    'INFO': 2,
    'WARNING': 3,
    'WARN': 3,
    'ERROR': 4
}

# default level
current_level='INFO'

def debug(*args):
    log(*args, level='DEBUG', stack=None)

def info(*args):
    log(*args, level='INFO', stack=None)

def warn(*args):
    log(*args, level='WARNING', stack=None)

def warning(*args):
    log(*args, level='WARNING', stack=None)

def error(*args):
    log(*args, level='ERROR', stack=None)

def log(*args, level, stack=None):
    global current_level

    if level not in LEVELS or LEVELS[level] < LEVELS[current_level]:
        return

    if stack == None:
        pass #stack = inspect.stack()[1]

    # [file/funcName:lineno loglevel] message
    print('[LOG %s]'
        % (LEVELS[level]),
        *args, file=sys.stderr)

def setLogLevel(level):
    global current_level

    if level in LEVELS:
        current_level = level

if __name__ == "__main__":
    setLogLevel('DEBUG')
    debug("FACK")

