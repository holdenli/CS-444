#!/usr/bin/python3

from scanner import Token
from utils.node import Node

def weed(parse_tree):

    if parse_tree.select(['ClassDeclaration']):
        node = parse_tree.select(['ClassDeclaration'])[0]

        # A class cannot be both abstract and final.
        if Node('Modifiers') in node.children:

            modifiers = node.children[node.children.index(Node('Modifiers'))]:
            leafs = modifiers.dfs_iter(leafs=True)

            if Node('Abstract') in leafs and Node('Final') in leafs:
                logging.error("A class cannot be both abstract and final.",
                    "pos=%d, line=%d", modifiers.value.pos, modifiers.value.line)
                sys.exit(42)

        # A method has a body if and only if it is neither abstract nor native.
        # An abstract method cannot be static or final.
        # A static method cannot be final.
        # A native method must be static.
        modifiers = node.select(['MethodHeader', 'Modifiers'])
        if modifiers:
            modifiers = modifiers[0].dfs_iter(leafs=True)
            is_abstract = Node('Abstract') in modifiers
            is_native = Node('Native') in modifiers
            is_static = Node('Static') in modifiers
            is_final = Node('Final') in modifiers

            abs_or_nat = is_abstract or is_native
            has_def = len(node.select(['MethodBody', 'Block'])) == 1

            if (has_def and abs_or_nat) or (not abs_or_nat and not has_def):
                logging.error("A method has a body if and only if it is neither abstract nor native.",
                    "pos=%d, line=%d", modifiers.value.pos, modifiers.value.line)
                sys.exit(42)

            elif is_abstract and (is_static or is_final):
                logging.error("An abstract method cannot be static or final.",
                    "pos=%d, line=%d", modifiers.value.pos, modifiers.value.line)
                sys.exit(42)

            elif is_static and is_final:
                logging.error("A static method cannot be final.",
                    "pos=%d, line=%d", modifiers.value.pos, modifiers.value.line)
                sys.exit(42)

            elif is_native and (not is_static):
                logging.error("A native method must be static",
                    "pos=%d, line=%d", modifiers.value.pos, modifiers.value.line)
                sys.exit(42)


        # Every class must contain at least one explicit constructor.
        class_name = node.children[node.index(Node('Identifier'))].value.value
        constructor_names = [method.value.value for method in node.select([
            'ConstructorDeclarator',
            'SimpleName',
            'Identifier'
        ])]

        if not constructor_names or
            [class_name]*len(constructor_names) != constructor_names:
            logging.error("Every class must contain at least one explicit constructor.",
                    "pos=%d, line=%d", node.value.pos, node.value.line)
            sys.exit(42)

        # No field can be final.
        fields = node.select(['FieldDeclaration', 'Modifiers'])
        for field in fields:
            modifiers = field.dfs_iter(leafs=True)
            if Node('Final') in modifiers:
                logging.error("No field can be final.",
                    "pos=%d, line=%d", modifiers.value.pos, modifiers.value.line)
                sys.exit(42)


    # An interface method cannot be static, final, or native.
    elif parse_tree.select(['InterfaceDeclaration']):
        modifiers = parse_tree.select([
            'InterfaceDeclaration',
            'InterfaceBody',
            'InterfaceMemberDeclarations',
            'InterfaceMemberDeclaration',
            'MethodHeader',
            'Modifiers'
        ]);

        for i in modifiers:
            mods = i.dfs_iter(leafs=True)
            if Node('Static') in mods or Node('Final') in mods or Node('Native') in mods:
                logging.error("An interface method cannot be static, final or native.",
                    "pos=%d, line=%d", i.value.pos, i.value.line)
                sys.exit(42)


        node.select(['Modifiers'])

# SOLVED BY GRAMMAR: The type void may only be uised as the return type of a method.
# WHAT IS THIS: A formal parameter of a method must not have an initializer.
# A class/interface must be declared in a .java file with the same base name as the class/interface.
# SOLVED BY GRAMMAR: An interface cannot contain fields or constructors.
# SOLVED BY GRAMMAR: An interface method cannot have a body.
# No multidimensional array types or array creation expressions are allowed.
# A method or constructor must not contain explicit this() or super() calls.
