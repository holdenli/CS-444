#!/usr/bin/python3

import inspect
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
    log(*args, level='DEBUG', stack=inspect.stack()[1])

def info(*args):
    log(*args, level='INFO', stack=inspect.stack()[1])

def warn(*args):
    log(*args, level='WARNING', stack=inspect.stack()[1])

def warning(*args):
    log(*args, level='WARNING', stack=inspect.stack()[1])

def error(*args):
    log(*args, level='ERROR', stack=inspect.stack()[1])

def log(*args, level, stack=None):
    global current_level

    if level not in LEVELS or LEVELS[level] < LEVELS[current_level]:
        return

    if stack == None:
        stack = inspect.stack()[1]

    # [file/funcName:lineno loglevel] message
    print('[%s:%s/%s %s]' % (os.path.basename(stack[1]), stack[2], stack[3], LEVELS[level]),
        *args, file=sys.stderr)

def setLogLevel(level):
    global current_level

    if level in LEVELS:
        current_level = level
