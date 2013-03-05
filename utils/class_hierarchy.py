#!/usr/bin/python3

import sys

import ast

from utils import logging

class Class:

    def __init__(self, name=''):
        self.name = name
        self.interface = False
        self.declare = {}
        self.inherit = {}
        self.replace = {}
        self.extends = None
        self.implements = None
        self.node = None
        self.env = None

    def __repr__(self):
        return "<Class: %s>" % self.name

def class_hierarchy(ast_list, env_list):
    class_dict = {}

    # scan ASTs for classes
    for a in ast_list:
        # figure out fully qualified name
        package = a[0][0]
        decl = a[0][3]
        name = decl[1][0].value.value
        name = ast.get_qualified_name(package) + "." + name
        if name[0] == ".":
            name = name[1:]

        # create class
        c = Class(name)
        c.node = decl
        c.interface = decl.name != "ClassDeclaration"
        c.extends = decl.find_child("Superclass")
        c.implements = decl.find_child("Interfaces")
        c.extends = ast.get_qualified_name(c.extends)
        c.implements = [ast.get_qualified_name(x) for x in c.implements.children]

        #decl.pprint()
        """
        print(c)
        print(c.interface)
        print("Extends:    ", c.extends)
        print("Implements: ", c.implements)
        """

        # TODO: check constraints on type info involving extends and implements
        if c.interface and False:
            logging.error("%s extend a class but is an interface" % name)
            sys.exit(42)

        if name in class_dict:
            logging.error("%s has already been declared." % name)
            sys.exit(42)

        class_dict[name] = c

    # create hiearchy
    for c in class_dict.values():
        if c.extends != "":
            if c.extends not in class_dict:
                logging.error("%s superclass does not exist (for %s)."
                    % (c.extends, c.name))
                sys.exit(42)
            else:
                c.extends = class_dict[c.extends]

        for i in c.implements:
            if i not in class_dict:
                logging.error("%s interface does not exist (for %s)."
                    % (i, c.name))
                sys.exit(42)
        c.implements = [class_dict[x] for x in c.implements]

    # check for cycles
    for c in class_dict.values():
        pass

# fill in declares

# fill in inherits

# fill in replaces
