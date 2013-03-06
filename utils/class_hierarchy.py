#!/usr/bin/python3

import sys

import ast

from utils import logging

class Field:
    def __init__(self, node, interface=False):
        if node == None or node.name != "FieldDeclaration":
            self.mods = []
            self.name = ""
            self.type = None
        else:
            self.mods = ast.get_modifiers(node.find_child("Modifiers"))
            self.name = node.find_child("Identifier").value.value
            self.type = ast.get_type(node.find_child("Type"))
        if interface:
            self.mods.append("Abstract")

    def __repr__(self):
        return "<Field: %s>" % self.name

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.name == other.name
        return False

class Method:
    def __init__(self, node, interface=False):
        if node == None or node.name != "MethodDeclaration":
            self.mods = []
            self.type = None
            self.name = ""
            self.params = []
        else:
            self.mods = ast.get_modifiers(node.find_child("Modifiers"))
            self.type = ast.get_type(node.find_child("Type"))
            self.name = node.find_child("Identifier").value.value
            self.params = ast.get_parameters(node.find_child("Parameters"))
        if interface:
            self.mods.append("Abstract")

    def __repr__(self):
        return "<Method: %s>" % self.name

    def __eq__(self, other):
        if isinstance(other, Method):
            return self.name == other.name and self.params == other.params
        return False

# Design notes:
#   - a "parallel bottom up tree structure" for super classes and interfaces
#   - no multiple inheritence means extends is not a list
#   - pointers to the relevant AST and ENV nodes
class Class:

    def __init__(self, name=''):
        self.name = name
        self.interface = False
        self.declare = []
        self.inherit = None
        self.extends = None
        self.implements = None
        self.node = None
        self.env = None

    def __repr__(self):
        return "<Class: %s>" % self.name

##########################

# helper methods

def cycle_detection(c, seen_so_far):
    l = list(c.implements)
    if c.extends != None:
        l.append(c.extends)
    
    for cc in l:
        if cc in seen_so_far:
            logging.error("Cycle detected in super class hierarchy for %s"
                % c.name)
            sys.exit(42)
        cycle_detection(cc, list(seen_so_far)+[cc])

##########################

# methods for resolving declare/inherit/replace

def contain(c):
    return c.declare + c.inherit

# m1 is replacing m2; do some checks
def replace(m1, list_of_m):
    if isinstance(m1, Field):
        return

    for m2 in list_of_m:
        # A nonstatic method must not replace a static method (JLS 8.4.6.1, dOvs well-formedness constraint 5) 
        if "Static" not in m1.mods and "Static" in m2.mods:
            logging.error("a nonstatic method (%s) replaced a static method (%s)" % (m1, m2))
            sys.exit(42)

        # A method must not replace a method with a different return type. (JLS 8.1.1.1, 8.4, 8.4.2, 8.4.6.3, 8.4.6.4, 9.2, 9.4.1, dOvs well-formedness constraint 6) 
        if m1.type != m2.type:
            logging.error("a method (%s) replaced a method (%s) with a different return type" % (m1, m2))
            sys.exit(42)

        # A protected method must not replace a public method. (JLS 8.4.6.3, dOvs well-formedness constraint 7) 
        if "Protected" in m1.mods and "Public" in m2.mods:
            logging.error("a protected method (%s) replaced a public method (%s)" % (m1, m2))
            sys.exit(42)

        # A method must not replace a final method. (JLS 8.4.3.3, dOvs well-formedness constraint 9) 
        if "Final" in m2.mods:
            logging.error("a method (%s) replaced a final method (%s)" % (m1, m2))
            sys.exit(42)

def determine_inherit(c):
    # make list of supers
    supers = list(c.implements)
    if c.extends != None:
        supers.append(c.extends)
    
    # make a list of all contains in supers
    super_contain = []
    for s in supers:
        super_contain.extend(contain(s))

    # now check everything in super_contain to see if it is inherited
    inherit = []
    for x in super_contain:
        # replace in declare: do not add to inherit because its in declare
        if x in c.declare:
            replace(x, [y for y in c.declare if y == x])
            continue

        # non-abstract inherit
        if x not in c.declare and "Abstract" not in x.mods:
            replace(x, [y for y in super_contain if y == x and "Abstract" in x.mods])
            inherit.append(x)
        # all abstract inherit
        elif x not in c.declare and False not in ["Abstract" in y.mods for y in super_contain if y == x]:
            replace(x, [y for y in super_contain if y == x])
            inherit.append(x)

    return inherit

##########################

# class_hierarchy
# creates all Classes, Fields, and Methods
# returns a dictionary of all available classes/interfaces
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
        else:
            c.extends = None

        for i in c.implements:
            if i not in class_dict:
                logging.error("%s interface does not exist (for %s)."
                    % (i, c.name))
                sys.exit(42)
        c.implements = [class_dict[x] for x in c.implements]

    # check for cycles
    for c in class_dict.values():
        cycle_detection(c, [])

    # create fields and methods and fill in declares
    for c in class_dict.values():
        # Fields
        fields = c.node.find_child("Fields")
        if fields != None: # Interfaces have no fields
            for f in fields:
                ff = Field(f, c.interface)
                if ff in c.declare:
                    logging.error("Duplicate declaration of field %s" % ff)
                    sys.exit(42)
                c.declare.append(ff)

        # Methods
        methods = c.node.find_child("Methods")
        for m in methods:
            mm = Method(m, c.interface)
            if mm in c.declare:
                logging.error("Duplicate declaration of method %s" % mm)
                sys.exit(42)
            c.declare.append(mm)

    # fill in inherits
    # Apologies for this code, but I'm just going to loop through the dictionary
    # until I have filled out all inherit data, since I don't want to create
    # a top-down tree structure for the class hierarchy
    continue_inherits = True
    while continue_inherits:
        continue_inherits = False
        for c in class_dict.values():
            if (c.extends != None and c.extends.inherit == None) or None in [x.inherit for x in c.implements]:
                continue_inherits = True
                continue
            elif c.inherit != None:
                continue
            else:
                c.inherit = determine_inherit(c)

# fill in replaces
