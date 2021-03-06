#!/usr/bin/python3

import logging
from utils.ast import *

class Node:

    def __init__(self, name=None, value=None, children=None):
        if children == None:
            children = []
        
        self.name = name
        self.value = value
        self.children = children
        
    def __repr__(self):
        if self.value != None:
            return "<Node: %s=%s>" % (self.name, self.value)
        else:
            return "<Node: %s>" % (self.name)

    def __eq__(self, other):
        return (other.__class__ == ASTNode or other.__class__ == Node) and (self.name == other.name)

    def __getitem__(self, key):
        return self.children[key]

    def find_child(self, token_name):
        for child in self.children:
            if child.name == token_name:
                return child
        return None

    def add(self, node):
        """
        Adds node to children (mostly for convenience).
        """
        self.children.append(node)

    @property
    def first(self):
        """
        Convenience getter for the first child.
        """
        return self.children[0]

    def bfs_iter(self, leafs=False):
        queue = [self]
        while len(queue) > 0:
            node = queue.pop(0)
            queue += node.children
            if leafs and len(node.children) != 0:
                continue

            yield node

    def dfs_iter(self, leafs=False):
        stack = [self]
        while len(stack) > 0:
            node = stack.pop(0)
            stack = node.children + stack
            if leafs and len(node.children) != 0:
                continue

            yield node

    def leafs(self):
        return list(self.dfs_iter(leafs=True))

    def leaf_values(self):
        return [l.value.value for l in self.leafs() if l.value != None]

    def select(self, names, deep=False, inclusive=True):
        """
        self.select(['ClassDeclaration', 'Modifiers'])
        
        will search through this node's heirarchy and return a list of all
        'Modifiers' nodes that have a ClassDeclaration->Modifiers structure
        in this node's subtree.
        
        """
        if inclusive:
            stack = [self]
            stack_counters = [0]
        else:
            stack = list(self.children)
            stack_counters = [0] * len(self.children)

        while len(stack) > 0:
            node = stack.pop(0)
            node_counter = stack_counters.pop(0)

            if node.name == names[node_counter]:
                node_counter += 1
                if node_counter == len(names):
                    yield node

                    if deep:
                        node_counter = 0
                    else:
                        continue
            else:
                node_counter = 0

            try:
                stack = node.children + stack
            except:
                print(stack)
                print(node, type(node.children))
                node.pprint()

            stack_counters = [node_counter]*len(node.children) + stack_counters

    def select_leaf_values(self, names):
        ret = []
        for s in self.select(names):
            ret.extend(i.value.value for i in s.leafs())

        return ret

    def pprint(self, tabsize=0):
        print(self.debug())
        
        return

        print(' '*tabsize, self)
        for c in self.children:
            c.pprint(tabsize=tabsize+2)

    def debug(self, level=None, verbose=True, prefix=""):
        s = prefix

        # Basic Info

        if isinstance(self, ASTNode):
            s += ":"
        else:
            s += "."
        
        s += "[%s]" % (self.name)
        
        # Verbose Info

        if not isinstance(self, ASTNode):
            if self.value != None:
                s += "='%s'" % (self.value.value)
            if hasattr(self, 'decl'):
                s += " decl='%s'" % (self.decl.name)
            if hasattr(self, 'canon'):
                s += " canon='%s'" % (self.canon)

        if self.name == "LocalVariableDeclaration":
            id_node = self.find_child("Identifier")
            if id_node != None and id_node.value != None:
                s += "='%s'" % (id_node.value.value)
            else:
                logging.warning("Node.debug: %s has an invalid identifier" % self.name)

        if verbose and (isinstance(self, ASTNode) or isinstance(self, Node)):
            
            members = self.__dict__;

            # Some useful stuff
            if self.name == "Root" or self.name == "CompilationUnit":
                c_node = get_class(self)
                if c_node == None:
                    logging.warning("Node.debug: could not find class decl for " + self.name)
                elif c_node.obj != None:
                    s += "='%s'" % c_node.obj.name 
            elif 'obj' in members and self.obj != None:
                    s += "='%s'" % self.obj.name 

            s += ">"

            # Additional Info

            if 'typ' in members and self.typ != None:
                if 'canon' in members and self.canon != None:
                    logging.warning("Node.debug: typ and canon appeared in " + self.name)
                s += " @typ: %s" % self.typ
            if 'canon' in members and self.canon != None:
                if self.name != "Type" and self.name != "ArrayType" and self.name != "Name":
                    logging.warning("Node.debug: canon appeared in " + self.name)
                s += " @canon: %s" % self.canon
            if 'env' in members and self.env != None:
                s += " @env"
            if 'obj' in members and self.obj != None:
                s += " @obj"
            if 'decl' in members and self.decl != None:
                s += " @decl"
            if 'decl_order' in members and self.decl_order != None:
                s += " @ord=%d" % self.decl_order
        else:
            s += ">"

        # Children

        if level != None:
            level -= 1

        if level == 0:
            s += " (...)"
            return s

        for c in self.children:
            new_prefix = prefix + ".   "
            s += "\n" + c.debug(level, verbose, new_prefix)
        
        return s

class ASTNode(Node):

    def __init__(self, name=None, value=None, children=None,
                env=None, decl=None, canon=None, modifiers=None,
                decl_order=None):

        super().__init__(name, value, children)

        if modifiers == None:
            modifiers = set()

        # used for FieldDeclaration, ConstructorDeclaration, MethodDeclaration
        # nodes, specifies the order in which they were declared (0 means declared
        # first)
        self.decl_order = decl_order

        # TYPE INFO

        # canonical type name; string
        # refers to a type name
        self.canon = canon

        # canonical type; string
        # refers to an expression with "typ"
        self.typ = None

        # LINKS: links to other structures

        self.env = env

        # Class/Method/Field object
        self.obj = None

        # Store a reference to a declaration (field, method, parameter, or local
        # variable) node. Only valid for certain types of expressions.
        self.decl = decl

        # Static analysis info
        self.reachable = None
        self.can_complete = None
        self.will_end = None

        # For code generation.
        self.label = None # For methods.
        self.frame_offset = None # for variable declaration/parameter nodes

        # DEPRECATED/MISC

        # set of modifier values for MethodDecl, ConstructorDecl, FieldDecl
        # e.g. set('public', 'static')
        self.modifiers = modifiers

    def __repr__(self):
        v = ""
        if self.value != None:
            v = "=%s" % self.value

        d = ""
        if self.decl != None:
            d = ' -> %s' % self.decl

        e = ""
        if self.env:
            e = " @env"

        c = ""
        if self.canon:
            c = " [canon=%s]" % self.canon

        t = ""
        if self.typ:
            t = " [typ=%s]" % self.typ

        o = ""
        if self.decl_order != None:
            o = " [order=%s]" % self.decl_order

        return "<ASTNode: %s%s%s%s%s%s%s>" % (self.name, v, d, e, c, t, o)

def find_nodes(tree, white_list):
    # we traverse through block_tree looking for any node in the white_list
    # we don't go past another Block, though
    ret = []
    for c in tree.children:
        if c in white_list:
            ret.append(c)
        else:
            ret.extend(find_nodes(c, white_list))

    return ret

