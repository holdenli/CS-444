#!/usr/bin/python3

from scanner import Token
from utils.node import Node

def weed(parse_tree):

    for node in parse_tree.dfs_iter():
        
        # A class cannot be both abstract and final.
        if node.name == 'ClassDeclaration' and \
            Node('Modifiers') in node.children:

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
        elif node.name == 'MethodDeclaration':
           modifiers = node.select(['MethodHeader', 'Modifiers'])[0].dfs_iter(leafs=True)
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
          


        # The type void may only be used as the return type of a method.
        # A formal parameter of a method must not have an initializer.
        # A class/interface must be declared in a .java file with the same base name as
        # the class/interface.
        # An interface cannot contain fields or constructors.
        # An interface method cannot be static, final, or native.
        # An interface method cannot have a body.
        # Every class must contain at least one explicit constructor.
        # No field can be final.
        # No multidimensional array types or array creation expressions are allowed.
        # A method or constructor must not contain explicit this() or super() calls.
