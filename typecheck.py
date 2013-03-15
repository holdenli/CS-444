import sys
from utils import logging
from utils import node
from utils import primitives

# gets a list of all nodes that need to be type checked
def get_exprs_from_node(n):
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
    exprs.extend(n.select(['ReturnStatement']))
    return exprs

def typecheck(type_index, class_index):
    for type_name, env in type_index.items():
        c = class_index[type_name]
        typecheck_methods(c, env, type_index, class_index)

def typecheck_methods(c, env, type_index, class_index):
    # interface has typecheck on field inits
    if c.interface:
        # TODO
        return

    # Run typecheck on each field
    for field_node in env['ClassDeclaration'].names.values():
        exprs = get_exprs_from_node(field_node)
        for expr in exprs:
            typecheck_expr(expr, c, env, None, type_index, class_index)

    # Run typecheck on each method
    for method_env in env['ClassDeclaration'].children:
        n = method_env.node
        exprs = get_exprs_from_node(n)
        for expr in exprs:
            t = n.find_child('Type')
            if t != None:
                t = t.canon
            typecheck_expr(expr, c, env, t, type_index, class_index)

#
# Type check functions.
# Each type check function must do the following:
# 1. Determine the correct type of the input node.
# 2. Assign the above type to the input node.
# 3. Return the assigned type, so that it can be used by the caller.

def typecheck_expr(node, c, class_env, return_type, type_index, class_index):
    # see if type for expr has already been resolved
    if hasattr(node, 'typ') and node.typ != None:
        return node.typ.name
    
    t = None

    # DO STUFF HERE...
    if node.name == 'PostfixExpression':
        z = node.find_child('Literal')
        if z != None:
            t = typecheck_literal(z, c, class_env, return_type, type_index)
        else:
            pass
    elif node.name == 'Assignment':
        pass
    elif node.name == 'MethodInvocation':
        pass
    elif node.name == 'ReturnStatement':
        typecheck_return(node, c, class_env, return_type, type_index, class_index)
    else:
        pass

    # set type
    node.typ = t

    # return the type
    if t != None:
        t = t.name
    return t

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

    rhs_type = typecheck_expression(node[1])

def typecheck_literal(node, c, class_env, return_type, type_index):
    if node.name != 'Literal':
        logging.error("FATAL ERROR: typecheck_literal") 
        sys.exit(1)
    
    # Check children to determine type.
    if node[0].name == 'DecimalIntegerLiteral':
        node.typ = primitives.get_type('Int')
    elif node[0].name == 'BooleanLiteral':
        node.typ = primitives.get_type('Boolean')
    elif node[0].name == 'CharacterLiteral':
        node.typ = primitives.get_type('Char')
    elif node[0].name == 'StringLiteral':
        node.typ = type_index['java.lang.String']
    elif node[0].name == 'NullLiteral':
        node.typ = primitives.get_type('Null')

    if node.typ == None:
        logging.error("FATAL ERROR?: Could not resolve literal.")
        sys.exit(1) # Could not resolve type, compiler error?

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
    elif not primitive.is_primitive(type1) and type2.name == 'Null':
        return True
    elif primitive.is_numeric(type1) and primitive.is_numeric(type2):
        return primitive.is_widening_conversion(type1, type2)
    elif not primitive.is_primitive(type1) and primitive.is_primitive(type2):
        return True
        # we require type2 <= type1 (type2 is a subclass of type1)
        #

def typecheck_return(node, c, class_env, return_type, type_index, class_index):
    if node.name != 'ReturnStatement':
        logging.error("FATAL ERROR: typecheck_return") 
        sys.exit(1)
    
    t = None
    if len(node.children) == 0:
        t = "Void"
    else:
        t = typecheck_expr(node.children[0], c, class_env, return_type, type_index, class_index)
    
    if t != return_type:
        #logging.error("typecheck failed:", node)
        #sys.exit(42)
        pass
    else:
        #logging.warning("typecheck passed", node)
        pass

    return t

