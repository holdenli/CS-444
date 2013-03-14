import sys
from utils import node
from utils import primitives

def typecheck(type_index, class_hierarchy):
    for fqtype, cu in enumerate(type_index):
        hierarchy = class_hierarchy[fqtype]
        typecheck_methods(cu, type_index, hierarchy)

def typecheck_methods(cu, type_index, hierarchy):
    for method in cu['ClassDeclaration'].methods:
        


# This function should be called for each statement in a method body.
def typecheck_statement(class_env, local_env, return_type, statement, type_index):
    if node.name == 

#
# Type check functions.
# Each type check function must do the following:
# 1. Determine the correct type of the input node.
# 2. Assign the above type to the input node.
# 3. Return the assigned type, so that it can be used by the caller.

# This function is called by typecheck_statement on a single expression.
def typecheck_expr(class_env, local_env, return_type, node, type_index):
    if node.name == 'Assignment':
        return typecheck_assignment(class_env, local_env, return_type, node)
    elif node.name == 'MethodInvocation':
        return typecheck_method_invo(class_env, local_env, return_type, node)

def typecheck_assignment(class_env, local_env, return_type, node):
    lhs_type = None
    if node[0].name == 'Name':
        lhs_type == get_typeof_name(node[0])
    elif node[0].name == 'FieldAccess':
        lhs_type == typecheck_field_access(node[0])
    elif node[0].name == 'ArrayAccess':
        lhs_type == typecheck_array_access(node[0])
    else:
    
        sys.exit(1) # should not happen

# def typecheck_array

def typecheck_literal(class_env, local_env, return_type, node, type_index):
    if node.name != 'Literal':
        sys.exit(42)
    
    # Check children to determine type.
    if node[0].name == 'DecimalIntegerLiteral':
        node.typ = primitives.get_type('int')
    elif node[0].name == 'BooleanLiteral':
        node.typ = primitives.get_type('boolean')
    elif node[0].name == 'CharacterLiteral':
        node.typ = primitives.get_type('char')
    elif node[0].name == 'StringLiteral':
        node.typ = type_index['java.lang.String']
    else
        node.typ = primitives.get_type('null')

    if node.typ == None:
        sys.exit(42) # Could not resolve type, compiler error?

    return node.typ

# Get the type from the input name node.
def typecheck_name(class_env, local_env, return_type, node, type_index):
    target_env = node.decl
    if target_env.name == '':
    elif target_env.name == 'ClassDeclaration':
    elif target_env.name == 'InterfaceDeclaration':
    
    return node.typ

# TODO: finish this
def is_assignable(type1, type2, class_env):
    if type1 == type2:
        return True
    if is_numeric(type1) and is_numeric(type2): # Widening conversions.
        return is_widening_conversion(type1, type2)
    elif type1 == 'int' and type2 in ['short', 'byte', 'char']:
        return True
    elif type1 == 'short' and type2 in ['byte', 'char']:
        return True
    elif type1 not in ['int', 'short', 'byte', 'char'] and type2 == 'null':
        return True


