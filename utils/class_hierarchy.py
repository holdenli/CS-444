#!/usr/bin/python3

import sys

import ast
import typelink

from utils import logging

class Field:
    def __init__(self, node, c):
        if node == None or node.name != "FieldDeclaration":
            self.mods = []
            self.name = ""
            self.type = None
        else:
            self.mods = ast.get_modifiers(node.find_child("Modifiers"))
            self.name = node.find_child("Identifier").value.value
            self.type = c.get_type(node.find_child("Type"))
        if c.interface:
            self.mods.append("Abstract")

    def __repr__(self):
        return "<Field: %s>" % self.name

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.name == other.name
        return False

# This is kinda overloaded to represent constructors as well cause I'm a terrible person
# When self.type == None, it is a constructor
class Method:
    def __init__(self, node, c):
        if node == None or (node.name != "MethodDeclaration" and node.name != "ConstructorDeclaration"):
            self.mods = []
            self.type = None
            self.name = ""
            self.params = []
        else:
            self.mods = ast.get_modifiers(node.find_child("Modifiers"))
            if node.name == "ConstructorDeclaration":
                self.type = None
            else:
                self.type = c.get_type(node.find_child("Type"))
            self.name = node.find_child("Identifier").value.value
            self.params = c.get_parameters(node.find_child("Parameters"))
        if c.interface:
            self.mods.append("Abstract")

    def __repr__(self):
        if (self.type == None):
            return "<Constructor: %s>" % self.name
        else:
            return "<Method: %s>" % self.name

    def __eq__(self, other):
        if isinstance(other, Method):
            if (self.type == None or other.type == None) and self.type != other.type:
                return False
            return self.name == other.name and self.params == other.params
        return False

# Design notes:
#   - a "parallel bottom up tree structure" for super classes and interfaces
#   - no multiple inheritence means extends is not a list
#   - pointers to the relevant AST and ENV nodes
class Class:

    def __init__(self, pkg, name):
        self.pkg = pkg
        self.name = pkg + "." + name
        if self.name[0] == ".":
            self.name = self.name[1:]
        
        self.interface = False
        self.mods = []
        
        self.declare = []
        self.inherit = None
        
        self.extends = None
        self.implements = None
        
        self.node = None
        self.env = None
        self.type_index = None

    def __repr__(self):
        return "<Class: %s>" % self.name

    def get_type(self, type_node):
        # preliminary checks on type_node
        if type_node == None or type_node.name != "Type":
            logging.error("FATAL ERROR: resolve_type")
            exit(1)

        # check for array
        isArray = type_node.find_child("ArrayType") != None
        if isArray:
            type_node = type_node.find_child("ArrayType")
        
        # not a reference type so return primitive or void
        if type_node.find_child("ReferenceType") == None:
            if isArray:
                return type_node.leafs()[0].value.value + "[]"
            else:
                return type_node.leafs()[0].value.value
        # reference type, resolve it
        else:
            t = typelink.resolve_type(self.type_index, self.env, self.pkg, type_node)
            if t != None and isArray:
                t = t + "[]"
            return t

    def get_parameters(self, node):
        if node == None:
            return []
        p = []
        for i in node.children:
            p.append(self.get_type(i.find_child("Type")))
        return p

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
        if ("Static" not in m1.mods and "Static" in m2.mods):
            logging.error("a nonstatic method (%s) replaced a static method (%s)" % (m1, m2))
            sys.exit(42)

        if ("Static" in m1.mods and "Static" not in m2.mods):
            logging.error("a static method (%s) replaced a nonstatic method (%s)" % (m1, m2))
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
            replace([z for z in c.declare if z == x][0],
                [y for y in super_contain if y == x])
            continue

        # non-abstract inherit
        if x not in c.declare and "Abstract" not in x.mods:
            replace(x, [y for y in super_contain if y == x and "Abstract" in y.mods])
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
def class_hierarchy(ast_list, pkg_index):
    type_index = typelink.build_canonical_type_index(pkg_index)

    class_dict = {}

    # scan ASTs for classes
    for a in ast_list:
        if len(a.children) == 0:
            continue

        # figure out fully qualified name
        package = a[0][0]
        pkg_name = ast.get_qualified_name(package)
        if pkg_name == "":
            pkg_name = "MAIN_PKG"
        decl = a[0][3]
        name = decl[1][0].value.value


        # create class
        c = Class(pkg_name, name)
        #print("@#", c.name)
        c.interface = decl.name != "ClassDeclaration"
        c.mods = ast.get_modifiers(decl.find_child("Modifiers"))
        
        c.extends = decl.find_child("Superclass")
        c.implements = decl.find_child("Interfaces")

        c.node = decl
        c.env = type_index[c.name]
        c.type_index = type_index

        tn = None
        if c.extends != None:
            tn = c.extends.find_child("Type")
        
        if tn != None:
            c.extends = typelink.resolve_type(c.type_index, c.env, c.pkg, tn)
        else:
            if c.interface == False and c.name != "java.lang.Object":
                c.extends = "java.lang.Object"
            else:
                c.extends = ""

        c.implements = [typelink.resolve_type(c.type_index, c.env, c.pkg, tn)
            for tn in c.implements.children]

        # An interface must not be repeated in an implements clause, or in an extends clause of an interface. (JLS 8.1.4, dOvs simple constraint 3) 
        for i in c.implements:
            if len([x for x in c.implements if x == i]) > 1:
                logging.error("%s is an interface that is repeated (for %s)."
                    % (i, c.name))
                sys.exit(42)
        
        #decl.pprint()
        """
        print(c)
        print(c.interface)
        print("Extends:    ", c.extends)
        print("Implements: ", c.implements)
        """

        if name in class_dict:
            logging.error("SHOULD NOT HAPPEN: %s has already been declared." % name)
            sys.exit(42)

        class_dict[c.name] = c

    # create hiearchy
    for c in class_dict.values():
        if c.extends != "":
            if c.extends not in class_dict:
                logging.error("%s superclass does not exist (for %s)."
                    % (c.extends, c.name))
                sys.exit(42)
            else:
                c.extends = class_dict[c.extends]
                # A class must not extend an interface. (JLS 8.1.3, dOvs simple constraint 1) 
                if c.extends.interface:
                    logging.error("%s is an interface (for %s)."
                        % (c.extends, c.name))
                    sys.exit(42)
                # A class must not extend a final class. (JLS 8.1.1.2, 8.1.3, dOvs simple constraint 4)
                if "Final" in c.extends.mods:
                    logging.error("%s is final and is extended (for %s)."
                        % (c.extends, c.name))
                    sys.exit(42)
                    
        else:
            c.extends = None

        for i in c.implements:
            if i not in class_dict:
                logging.error("%s interface does not exist (for %s)."
                    % (i, c.name))
                sys.exit(42)
        c.implements = [class_dict[x] for x in c.implements]
        for i in c.implements:
            # A class must not implement a class. (JLS 8.1.4, dOvs simple constraint 2) 
            # An interface must not extend a class. (JLS 9.1.2) 
            if i.interface != True:
                logging.error("%s is not an interface (for %s)."
                    % (i, c.name))
                sys.exit(42)

    # check for cycles
    # The hierarchy must be acyclic. (JLS 8.1.3, 9.1.2, dOvs well-formedness constraint 1) 
    for c in class_dict.values():
        cycle_detection(c, [])

    # create fields and methods and fill in declares
    for c in class_dict.values():
        # Fields
        fields = c.node.find_child("Fields")
        if fields != None: # Interfaces have no fields
            for f in fields:
                ff = Field(f, c)
                if ff in c.declare:
                    logging.error("Duplicate declaration of field %s" % ff)
                    sys.exit(42)
                c.declare.append(ff)

        # Methods
        methods = c.node.find_child("Methods")
        for m in methods:
            mm = Method(m, c)
            # A class or interface must not declare two methods with the same signature (name and parameter types). (JLS 8.4, 9.4, dOvs well-formedness constraint 2) 
            # A class or interface must not contain (declare or inherit) two methods with the same signature but different return types (JLS 8.1.1.1, 8.4, 8.4.2, 8.4.6.3, 8.4.6.4, 9.2, 9.4.1, dOvs well-formedness constraint 3) 
            if mm in c.declare:
                logging.error("Duplicate declaration of method %s" % mm)
                sys.exit(42)
            c.declare.append(mm)

        # Constructors
        constructors = c.node.find_child("Constructors")
        if constructors == None:
            constructors = []
        for con in constructors:
            ccon = Method(con, c)
            # A class must not declare two constructors with the same parameter types (dOvs 8.8.2, simple constraint 5) 
            if ccon in c.declare:
                logging.error("Duplicate declaration of constructor %s" % ccon)
                sys.exit(42)
            c.declare.append(ccon)

        # annoying edge case check yo
        if c.interface:
            m = Method(None, c)
            m.type = "java.lang.Class"
            m.name = "getClass"
            m.params = []
            if m in c.declare:
                logging.error("interface declared a final method:", m)
                sys.exit(42)

        # Implicit declare for interface without superinterface
        if c.interface and len(c.implements) == 0:
            # Add publics of java.lang.Object
            for (n, t) in [
                    ("equals", "boolean"),
                    ("toString", "java.lang.String"),
                    ("hashCode", "int"),
                    ("getClass", "java.lang.Class")
                    ]:
                m = Method(None, c)
                m.mods = ["Public", "Abstract"]
                m.type = t
                m.name = n
                m.params = []
                if (n == "equals"):
                    m.params.append("java.lang.Object")
                elif (n == "getClass"):
                    pass
                if m not in c.declare:
                    c.declare.append(m)
                elif m.type not in [x.type for x in c.declare if x == m]:
                    logging.error("Implicit decl of %s return type does not match" % m)
                    sys.exit(42)

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

    # final checks
    for c in class_dict.values():
        # A class that contains (declares or inherits) any abstract methods must be abstract. (JLS 8.1.1.1, well-formedness constraint 4)
        if c.interface != True and "Abstract" not in c.mods and True in [True for x in contain(c) if "Abstract" in x.mods]:
            logging.error("%s is not abstract but contains an abstract method" % c)
            sys.exit(42)

