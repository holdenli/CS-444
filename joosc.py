#!/usr/bin/python3

import sys
import optparse
import os
import pprint
from utils import logging
from utils import options as opts
from utils.options import JooscOptions

import test
import scanner
import parser
import weeder
import ast
from utils import class_hierarchy

from environment import build_environments
import typelink
import typecheck
import name_resolve

# Globals
##########################

parse_table = parser.read_parse_table('grammar.lr1')
stdlib_asts = None

# COMPILING
##########################

# Invokes the scanner for the input program.
def get_tokens(filename, options):
    tokens = None
    with open(filename, 'r') as f:
        tokens = scanner.scan(f.read())

    if options.stage == 'scanner':
        # If stdlib files were not included, we print regardless.
        # Otherwise, print only if it's not an stdlib file, unless overridden
        # by JooscOptions.print_stdlib.
        if options.include_stdlib == False or filename not in opts.stdlib_files or \
                options.print_stdlib == True:
            print("Tokens returned from scanner for %s:\n" % filename,
                pprint.pformat(tokens))

    return tokens

def get_parse_tree(tokens, filename, options):
    global parse_table

    parse_tree = parser.parse(tokens, parse_table)
    if parse_tree == False:
        logging.error("Could not parse file %s" % filename)
        sys.exit(42)

    if options.stage == 'parser':
        if options.include_stdlib == False or filename not in opts.stdlib_files or \
                options.print_stdlib == True:
            print("Unweeded parse tree for %s:" % filename)
            parse_tree.pprint()

    return parse_tree

def weed_parse_tree(parse_tree, filename, options):
    weeder.weed(parse_tree, filename)

    if options.stage == 'weeder':
        if options.include_stdlib == False or filename not in opts.stdlib_files or \
                options.print_stdlib == True:
            print("Weeded parse tree for %s:" % filename)
            parse_tree.pprint()

def get_ast(parse_tree, filename, options):
    abstract_syntax_tree = ast.build_ast(parse_tree)
    if options.stage == 'ast':
        if options.include_stdlib == False or filename not in opts.stdlib_files or \
                options.print_stdlib == True:
            abstract_syntax_tree.pprint()

    return abstract_syntax_tree

# Main work
def joosc(targets, options):
    
    # SETUP
    ########

    global stdlib_asts

    # Build a list of targets to compile.
    target_files = []
    for target in targets:
        if os.path.isfile(target) and target.endswith('.java'):
            target_files.append(target)
        elif os.path.isdir(target) and options.directory_crawl == True:
            target_files.extend(opts.directory_crawl(target))
        else:
            logging.error("Invalid target %s, exiting..." % target)

    if options.include_stdlib == True and stdlib_asts == None:
        target_files.extend(opts.stdlib_files)

    # BUILD AST
    ############

    # Build token list for each file.
    token_lists = []
    for target_file in target_files:
        token_lists.append(get_tokens(target_file, options))
    if options.stage == 'scanner':
        sys.exit(0)

    # Build parse trees for each file.
    parse_trees = []
    for i, tokens in enumerate(token_lists):
        parse_trees.append(get_parse_tree(tokens, target_files[i], options))
    if options.stage == 'parser':
        sys.exit(0)

    # Weed each parse tree.
    for i, parse_tree in enumerate(parse_trees):
        weed_parse_tree(parse_tree, target_files[i], options)
    if options.stage == 'weeder':
        sys.exit(0)

    ast_list = []
    for i, parse_tree in enumerate(parse_trees):
        ast_list.append(get_ast(parse_tree, target_files[i], options))
    if options.stage == 'ast':
        sys.exit(0)

    # stdlib optimization
    if options.include_stdlib == True:
        if stdlib_asts != None:
            ast_list.extend(stdlib_asts)
        else:
            stdlib_asts = []
            for i, ast in enumerate(ast_list):
                if target_files[i] in opts.stdlib_files:
                    stdlib_asts.append(ast)

    # TYPE RESOLUTION
    ##################

    pkg_index = build_environments(ast_list)
    
    type_index = typelink.typelink(ast_list, pkg_index)

    class_index = class_hierarchy.class_hierarchy(ast_list, pkg_index, type_index)
    if options.stage == 'hierarchy':
        sys.exit(0)

    name_resolve.name_link(pkg_index, type_index, class_index)
    if options.stage == 'name':
        for i, _ in enumerate(ast_list): 
            if options.include_stdlib == False or target_files[i] not in opts.stdlib_files or \
                    options.print_stdlib == True:
                ast_list[i].pprint()
        sys.exit(0)

    typecheck.typecheck(type_index, class_index)

# INTERFACE
##########################

def parse_options(args=sys.argv):
    parser = optparse.OptionParser()

    #
    # Global options.
    #
    parser.add_option('-l', '--loglevel', action='store', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help="""Logging level. Choices: DEBUG, INFO, WARNING, ERROR.
            [default: WARNING]""")

    #
    # Options for compilation (joosc).
    #
    stage_opts = [
        'scanner',
        'parser',
        'weeder',
        'ast',
        'hierarchy',
        'name',
        'end'
    ]
    parser.add_option('-s', '--stage', action='store', dest='stage',
        default='end', choices=stage_opts,
        help="Stage of compiler to run \"up to\" before terminating.")

    parser.add_option('-i', '--include_stdlib', action='store_true',
        dest='include_stdlib', help="Include all stdlib files in compilation")

    parser.add_option('--print_stdlib', action='store_true',
        dest='print_stdlib',
        help="""Override default hiding of output printout for stdlib files.
            Only has any effect if -s and -i are specified.""")

    parser.add_option('-d', '--directory_crawl', action='store_true',
        dest='directory_crawl',
        help="Recursively crawl directories for compilation units")

    #
    # Options for testing.
    #

    parser.add_option('-t', '--test', action='store', dest='test',
        help="Run tests under the specified directory under assignment_testcases.")

    parser.add_option('--show_errors', action='store_true',
        dest='show_errors',
        help="Disable stderr printout suppression. Only usable during tests.")

    return parser.parse_args()

def main(argv=sys.argv):
    (opts, args) = parse_options(argv)

    logging.setLogLevel(level=opts.loglevel)

    joosc_opts = JooscOptions(opts.stage, opts.include_stdlib == True,
        opts.print_stdlib == True, opts.directory_crawl == True)
    
    if opts.test:
        logging.info("TESTING %s" % (opts.test))

        # TODO: Decide when to toggle verbose. Old method was insufficient.
        test.setup_and_run(opts.test, opts.show_errors == True, False,
            joosc_opts)
        return 0
 
    if len(args) < 1:
        logging.info("Nothing to compile.")
        return 0

    joosc(args, joosc_opts)

if __name__ == "__main__":
    try:
        main()
        logging.info("compiled successfully")
    except SystemExit as e:
        logging.info("exited with %d" % e.code)
        sys.exit(e.code)

