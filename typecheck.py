import sys
from utils import node

def typecheck(type_index, class_hierarchy):
    for fqtype, cu in enumerate(type_index):
        hierarchy = class_hierarchy[fqtype]
        typecheck_methods(cu, type_index, hierarchy)

def typecheck_methods(cu, type_index, hierarchy):
    for method in cu['ClassDeclaration'].methods:
        


# This function should be called for each statement in a method body.
def typecheck_statement(class_env, local_env, return_type, statement):
    pass

#
# Type check functions.
# Each type check function must do the following:
# 1. Determine the correct type of the input node.
# 2. Assign the above type to the input node.
# 3. Return the assigned type, so that it can be used by the caller.

# This function is called by typecheck_statement on a single expression.
def typecheck(class_env, local_env, return_type, node):
    pass

def typecheck_literal(class_env, local_env, return_type, node):
    if node.name != 'Literal':
        sys.exit(42)
    
    # Check children to determine type.
    if node[0].name == 'DecimalIntegerLiteral':
        node.typ = Node('int')
    elif node[0].name == 'BooleanLiteral':
        node.typ = Node('boolean')
    elif node[0].name == 'CharacterLiteral':
        node.typ = Node('char')
    elif node[0].name == 'StringLiteral':
        node.typ = type_index['java.lang.String']
    else
        node.typ = Node('null')

    return node.typ

