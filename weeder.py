#!/usr/bin/python3

import os
import sys

from utils import logging

from scanner import Token
from utils.node import Node

# TODO: Investigate Package Private classes, interfaces, fields
# Basic a1 tests do not fully cover these cases

# SOLVED BY GRAMMAR: The type void may only be uised as the return type of a method.
# SOLVED BY GRAMMAR: A class/interface must be declared in a .java file with the same base name as the class/interface.
# SOLVED BY GRAMMAR: An interface cannot contain fields or constructors.
# SOLVED BY GRAMMAR: An interface method cannot have a body.
# SOVLED BY GRAMMAR: A method or constructor must not contain explicit this() or super() calls.
# SOLVED BY GRAMMAR: No multidimensional array types or array creation expressions are allowed.

def weed(parse_tree, filename):

    # Problem 5: Cast versus Parenthesized Expression
    cast_exprs = parse_tree.select(['CastExpression', 'Expression'], deep=True)
    correct_cast_hiearchy = [
        'AssignmentExpression', 
        'ConditionalExpression', 
        'ConditionalOrExpression', 
        'ConditionalAndExpression', 
        'InclusiveOrExpression', 
        'ExclusiveOrExpression', 
        'AndExpression', 
        'EqualityExpression', 
        'RelationalExpression', 
        'ShiftExpression', 
        'AdditiveExpression', 
        'MultiplicativeExpression', 
        'UnaryExpression', 
        'UnaryExpressionNotPlusMinus', 
        'PostfixExpression', 
        'Name']
    for e in cast_exprs:
        c = [e]
        for name in correct_cast_hiearchy:
            c = c[0].children
            if len(c) != 1 or c[0].name != name:
                logging.error("Incorrect cast expression", e.leafs())
                sys.exit(42)

    # BOUNDS CHECKING WEEDING:
    unarys = list(parse_tree.select(['UnaryExpression']))
    for unary in unarys:
        leafs = unary.leafs()

        # Bounds checking on negative integers
        if len(leafs) == 2 \
            and leafs[0] == Node('SubtractOperator') \
            and leafs[1] == Node('DecimalIntegerLiteral'):
            
            if int(leafs[1].value.value) > 2147483648:
                logging.error("Integer out of bounds: -%s" % leafs[1].value.value,
                    "pos=%s, line=%s" % (leafs[1].value.pos, leafs[1].value.line))
                sys.exit(42)
        
        # Bounds checking on positive integers 
        elif len(leafs) == 1 \
            and leafs[0] == Node('DecimalIntegerLiteral'):

            if int(leafs[0].value.value) > 2147483647:
                logging.error("Integer out of bounds: %s" % leafs[0].value.value,
                            "pos=%s, line=%s" % (leafs[0].value.pos, leafs[0].value.line))
                sys.exit(42)
        else:
            unarys.extend(unary.select(['UnaryExpression'], inclusive=False))

    # WEEDING RELATED TO CLASSES:
    classes = list(parse_tree.select(['ClassDeclaration']))
    if len(classes) != 0:
        node = classes[0]
        classname = node.find_child('Identifier').value.value

        # A class/interface must be declared in a .java file with the same base name
        # as the class/interface.
        if os.path.basename(filename) != '%s.java' % classname:
            logging.error("A class must be declared in a .java file with the same base name as the class.")
            sys.exit(42)

        # A class cannot be both abstract and final.
        if Node('Modifiers') in node.children:

            modifiers = node.find_child('Modifiers').leafs()

            if Node('Abstract') in modifiers and Node('Final') in modifiers:
                logging.error("A class cannot be both abstract and final.",
                    "pos=%s, line=%s" % (modifiers[0].value.pos, modifiers[0].value.line))
                sys.exit(42)

        # A method has a body if and only if it is neither abstract nor native.
        # An abstract method cannot be static or final.
        # A static method cannot be final.
        # A native method must be static.
        methods = node.select(['ClassMemberDeclaration', 'MethodDeclaration'])
        for method in methods:
            modifiers = list(method.select(['MethodHeader','Modifiers']))
            if len(modifiers) == 0:
                continue

            modifiers = modifiers[0].leafs()
            is_abstract = Node('Abstract') in modifiers
            is_native = Node('Native') in modifiers
            is_static = Node('Static') in modifiers
            is_final = Node('Final') in modifiers
            is_public = Node('Public') in modifiers
            is_protected = Node('Protected') in modifiers

            abs_or_nat = is_abstract or is_native
            has_def = len(list(method.select(['MethodBody', 'Block']))) == 1

            if (has_def and abs_or_nat) or (not abs_or_nat and not has_def):
                logging.error("A method has a body if and only if it is neither abstract nor native.",
                    "pos=%s, line=%s" % (modifiers[0].value.pos, modifiers[0].value.line))
                sys.exit(42)

            elif is_abstract and (is_static or is_final):
                logging.error("An abstract method cannot be static or final.",
                    "pos=%s, line=%s" % (modifiers[0].value.pos, modifiers[0].value.line))
                sys.exit(42)

            elif is_static and is_final:
                logging.error("A static method cannot be final.",
                    "pos=%s, line=%s" % (modifiers[0].value.pos, modifiers[0].value.line))
                sys.exit(42)

            elif is_native and (not is_static):
                logging.error("A native method must be static",
                    "pos=%s, line=%s" % (modifiers[0].value.pos, modifiers[0].value.line))
                sys.exit(42)

            elif not (is_public or is_protected):
                logging.error("Method cannot be package-private",
                    "pos=%s, line=%s" % (modifiers[0].value.pos, modifiers[0].value.line))
                sys.exit(42)

        for constructor in node.select(['ConstructorDeclaration']):

            # Every class must contain at least one explicit constructor.
            constructor_names = [method.value.value for method in node.select([
                'ConstructorDeclarator',
                'SimpleName',
                'Identifier'
            ])]

            if not constructor_names or \
                [classname]*len(constructor_names) != constructor_names:
                logging.error("Every class must contain at least one explicit constructor.",
                        "Class %s does not." % (classname)),
                sys.exit(42)

            # Constructors can only be public or protected
            modifiers = list(constructor.select(['ConstructorDeclaration', 'Modifiers']))
            if len(modifiers) == 0:
                continue
            
            modifiers = modifiers[0].leafs()
            mod_count = 0
            if Node('Public') in modifiers: mod_count += 1
            if Node('Protected') in modifiers: mod_count += 1
            if mod_count != len(modifiers):
                logging.error("Constructors can only be public or protected.",
                    "pos=%s, line=%s" % (modifiers[0].value.pos, modifiers[0].value.line))
                sys.exit(42)



        # No field can be final.
        fields = node.select(['FieldDeclaration', 'Modifiers'])
        for field in fields:
            modifiers = field.leafs()
            if Node('Final') in modifiers:
                logging.error("No field can be final.",
                    "pos=%s, line=%s" % (modifiers[0].value.pos, modifiers[0].value.line))
                sys.exit(42)

    # WEEDING RELATED TO INTERFACES:
    # An interface method cannot be static, final, or native.
    elif len(list(parse_tree.select(['InterfaceDeclaration']))) != 0:

        interfacename = list(parse_tree.select(['InterfaceDeclaration',
            'Identifier']))[0].value.value

        # A class/interface must be declared in a .java file with the same base name
        # as the class/interface.
        if os.path.basename(filename) != '%s.java' % interfacename:
            logging.error("A interface must be declared in a .java file with the same base name as the interface.")
            sys.exit(42)

        modifiers = parse_tree.select([
            'InterfaceDeclaration',
            'InterfaceBody',
            'InterfaceMemberDeclarations',
            'InterfaceMemberDeclaration',
            'MethodHeader',
            'Modifiers'
        ]);

        for i in modifiers:
            mods = i.leafs()
            if Node('Static') in mods or Node('Final') in mods or Node('Native') in mods:
                logging.error("An interface method cannot be static, final or native.",
                    "pos=%s, line=%s" % (mods[0].value.pos, mods[0].value.line))
                sys.exit(42)
