#!/usr/bin/python3

import sys

import ast

from utils import logging
from utils import node
from utils import class_hierarchy

# METHOD TABLE
###############################################################################

def build_constructor_index(class_index):
    method_index = []
    for c in class_index.values():
        for m in c.declare:
            if isinstance(m, class_hierarchy.Method) and m.type == None:
                if m not in method_index:
                    method_index.append(m)

    return method_index

def build_method_index(class_index):
    method_index = []
    for c in class_index.values():
        for m in c.declare:
            if isinstance(m, class_hierarchy.Method) \
                and m.type != None \
                and 'Static' not in m.mods:
                if m not in method_index:
                    method_index.append(m)

    return method_index

# Generates assembly for the selector index table. We generate one of these per
# class/file.
def gen_sit(method_index, c):
    contain = class_hierarchy.contain(c)
    output = []
    
    output.append("SIT~%s:" % c.name)
    #output.append("dd SBM~%s" % c.name)
    for m in method_index:
        if m in contain:
            i = contain.index(m)
            actual_m = contain[i]
            output.append("dd %s ; %s | %s" % (actual_m.node.label, c.name, actual_m.name))
        else:
            output.append("dd 0")

    return output

# SUPERCLASS MATRIX
###############################################################################

def is_supertype(supertype, c):
    if supertype == None or c == None:
        return False

    if supertype == c:
        return True

    if (is_supertype(supertype, c.extends)):
        return True

    for i in c.implements:
        if (is_supertype(supertype, i)):
            return True

    return False

def build_class_list(class_index):
    return list(class_index.values())

def gen_sbm(class_list, c):
    #print(c)
    matrix_list = []
    digit = 0
    chunk = 0
    for cc in class_list:
        if digit >= 16:
            matrix_list.append(chunk)
            digit = 0
            chunk = 0
        if is_supertype(cc, c):
            #print(cc)
            chunk = chunk | (1 << (15 - digit))
        digit = digit + 1 
    matrix_list.append(chunk)
    #print(matrix_list)

    output = []
    output.append("SBM~%s:" % c.name)
    for i in matrix_list:
        output.append("dd %i" % i)

    return output

# FIELDS
###############################################################################

# Get fields in the order they are declared in the hierarchy
def get_all_fields(c):
    fields = []

    if c.extends == None:
        fields = c.declare
    else:
        fields = get_all_fields(c.extends)
        fields.extend(c.declare)

    ret = []
    for f in [x for x in fields if isinstance(x, class_hierarchy.Field)]:
        if f not in ret:
            ret.append(f)

    return ret 

# A dictionary where key is class name and
# value is list of field names in that class
def build_field_index(class_index):
    field_index = {}
    for c in class_index.values():
#        print(c)
        field_index[c.name] = []
        for m in get_all_fields(c):
            if isinstance(m, class_hierarchy.Field):
                field_index[c.name].append(m)
#                print(" ",field_index[c.name].index(m), field_index[c.name])
            else:
                logging.error("build_field_index")
                sys.exit(1)

    return field_index

