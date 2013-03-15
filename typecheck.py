import sys
from utils import node
from utils import primitives

def typecheck(type_index, class_index):
    for type_name, env in type_index.items():
        c = class_index[type_name]
        typecheck_methods(c, env, type_index)

def typecheck_methods(c, env, type_index):
    if c.interface:
        return
    for method_env in env['ClassDeclaration'].children:
        n = method_env.node
        exprs = []
        exprs.extend(n.select(['Assignment']))
        exprs.extend(n.select(['MethodInvocation']))
        exprs.extend(n.select(['CreationExpression']))
        exprs.extend(n.select(['ConditionalOrExpression']))
        exprs.extend(n.select(['ConditionalAndExpression']))
        exprs.extend(n.select(['InclusiveOrExpression']))
        exprs.extend(n.select(['ExclusiveOrExpression']))
        exprs.extend(n.select(['AndExpression']))
        exprs.extend(n.select(['EqualityExpression']))
        exprs.extend(n.select(['AdditiveExpression']))
        exprs.extend(n.select(['MultiplicativeExpression']))
        exprs.extend(n.select(['RelationalExpression']))
        exprs.extend(n.select(['InstanceofExpression']))
        exprs.extend(n.select(['UnaryExpression']))
        exprs.extend(n.select(['PostfixExpression']))
        exprs.extend(n.select(['CastExpression']))
        for expr in exprs:
            typecheck_expr(expr, c, env, type_index)
#
# Type check functions.
# Each type check function must do the following:
# 1. Determine the correct type of the input node.
# 2. Assign the above type to the input node.
# 3. Return the assigned type, so that it can be used by the caller.

def typecheck_expr(node, c, class_env, type_index):
    """
    if node.name == 'Assignment':
        return typecheck_assignment(class_env, local_env, return_type, node)
    elif node.name == 'MethodInvocation':
        return typecheck_method_invo(class_env, local_env, return_type, node)
    """

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
    else:
        node.typ = primitives.get_type('null')

    if node.typ == None:
        sys.exit(42) # Could not resolve type, compiler error?

    return node.typ

# Get the type from the input name node.
def typecheck_name(class_env, local_env, return_type, node, type_index):
    target_env = node.decl
    if target_env.name == '':
        pass
    elif target_env.name == 'ClassDeclaration':
        pass
    elif target_env.name == 'InterfaceDeclaration':
        pass
    
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

