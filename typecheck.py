import sys
from utils import logging
from utils import node
from utils import primitives

# Note: I'm going to call some statements expressions cause why not?
# ie. ReturnStatement

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

    # statement "exprs"
    exprs.extend(n.select(['ReturnStatement']))
    exprs.extend(n.select(['IfStatement']))
    exprs.extend(n.select(['WhileStatement']))
    exprs.extend(n.select(['ForStatement']))
    return exprs

def isNumType(t):
    return t == "Byte" or t == "Char" or t == "Short" or t == "Int"

def typecheck(t_i, c_i):
    for type_name, env in t_i.items():
        c = c_i[type_name]
        typecheck_methods(c, env, t_i, c_i)

def typecheck_methods(c, env, t_i, c_i):
    # interface has typecheck on field inits
    if c.interface:
        # TODO
        return

    # Run typecheck on each field
    for field_node in env['ClassDeclaration'].names.values():
        exprs = get_exprs_from_node(field_node)
        for expr in exprs:
            typecheck_expr(expr, c, env, None, t_i, c_i)

    # Run typecheck on each method
    for method_env in env['ClassDeclaration'].children:
        n = method_env.node
        exprs = get_exprs_from_node(n)
        for expr in exprs:
            t = n.find_child('Type')
            if t != None:
                t = t.canon
            typecheck_expr(expr, c, env, t, t_i, c_i)

#
# Type check functions.
# Each type check function must do the following:
# 1. Determine the correct type of the input node.
# 2. Assign the above type to the input node.
# 3. Return the assigned type, so that it can be used by the caller.

def typecheck_expr(node, c, class_env, return_type, t_i, c_i):
    # see if type for expr has already been resolved
    if hasattr(node, 'typ') and node.typ != None:
        return node.typ
    
    t = None

    # DO STUFF HERE...
    if node.name == 'Assignment':
        pass
    elif node.name == 'MethodInvocation':
        pass
    elif node.name == 'CreationExpression':
        pass
    elif node.name == 'ConditionalOrExpression':
        pass
    elif node.name == 'ConditionalAndExpression':
        pass
    elif node.name == 'InclusiveOrExpression':
        pass
    elif node.name == 'ExclusiveOrExpression':
        pass
    elif node.name == 'AndExpression':
        pass
    elif node.name == 'EqualityExpression':
        pass
    elif node.name == 'AdditiveExpression':
        t = typecheck_add(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'MultiplicativeExpression':
        t = typecheck_mult(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'UnaryExpression':
        t = typecheck_unary(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'PostfixExpression':
        z = node.find_child('Literal')
        if z != None:
            t = typecheck_literal(z, c, class_env, return_type, t_i)
        else:
            pass

    elif node.name == 'ReturnStatement':
        t = typecheck_return(node, c, class_env, return_type, t_i, c_i)
    else:
        pass

    # set type
    node.typ = t

    # return the type
    return t

# def typecheck_primary(node, c, class_env, return_type, type_index, class_dict):


def typecheck_assignment(class_env, local_env, return_type, node):
    lhs_type = None
    if node[0].name == 'Name':
        lhs_type == get_typeof_name(node[0])
    elif node[0].name == 'FieldAccess':
        lhs_type == typecheck_field_access(node[0])
    elif node[0].name == 'ArrayAccess':
        lhs_type == typecheck_array_access(node[0])
    else:
        logging.error('FATAL ERROR: Invalid typecheck_assignment')
        sys.exit(1) # should not happen

    rhs_type = typecheck_expr(node[1])
    
    if is_assignable(lhs_type, rhs_type, class_dict):
        node.typ = lhs_type
    else:
        logging.error('Cannot assign expression of type %s to LHS of type %s' %
            rhs_type.canon, lhs_type.canon)
        sys.exit(42)
    return node.typ

def typecheck_cast_expression(node, class_dict, class_env, return_type):
    if node.name != 'CastExpression':
        logging.error('FATAL: Invalid node %s for typecheck_cast_expression' %
            node.name)
        sys.exit(1)

    expr_type = typecheck_expr(node[1])
    if is_assignable(expr_type, node[0]) or is_assignable(node[0], expr_type):
        node.typ = node[0].typ
        return node.typ
    else:
        logging.error('Cast expression of type %s into %s invalid' %
            (expr_type.canon, node[0].canon))
        sys.exit(42)

def typecheck_literal(node, c, class_env, return_type, t_i):
    if node.name != 'Literal':
        logging.error('FATAL ERROR: Invalid node %s for typecheck_literal' %
            node.name)
        sys.exit(1)
    
    # Check children to determine type.
    if node[0].name == 'DecimalIntegerLiteral':
        node.typ = primitives.get_type('Int')
    elif node[0].name == 'BooleanLiteral':
        node.typ = primitives.get_type('Boolean')
    elif node[0].name == 'CharacterLiteral':
        node.typ = primitives.get_type('Char')
    elif node[0].name == 'StringLiteral':
        node.typ = t_i['java.lang.String']
    elif node[0].name == 'NullLiteral':
        node.typ = primitives.get_type('Null')

    if node.typ == None:
        logging.error("FATAL ERROR?: Could not resolve literal.")
        sys.exit(1) # Could not resolve type, compiler error?

    return node.typ

# Get the type from the input name node.
def typecheck_name(class_env, local_env, return_type, node, t_i):
    target_env = node.decl
    if target_env.name == '':
        pass
    elif target_env.name == 'ClassDeclaration':
        pass
    elif target_env.name == 'InterfaceDeclaration':
        pass
    
    return node.typ

def is_assignable(type1, type2, class_dict):
    if type1.canon == type2.canon:
        return True
    elif not primitive.is_primitive(type1) and type2.name == 'Null':
        return True
    elif primitive.is_numeric(type1) and primitive.is_numeric(type2):
        return primitive.is_widening_conversion(type1, type2)
    elif not primitive.is_primitive(type1) and primitive.is_primitive(type2):
        return is_nonstrict_subclass(type2, type1, class_dict)
    else:
        return False


# Returns True if type1 and type2 refer to the same class, or 
def is_nonstrict_subclass(type1, type2, class_dict):
    # Do a BFS up the hierarchy.
    queue = [type2.canon]
    while len(queue) > 0:
        typename = queue.pop(0)

        # Found type1 as a superclass of type2.
        if type1.canon == typename:
            return True
        else:
            cls = class_dict[typename]
            queue.extend(list(cls.implements))
            if cls.extends != None:
                queue.append(cls.extends)

    # Did not find type1 as a superclass of type2.
    return False

# Operators

def typecheck_unary(node, c, class_env, return_type, t_i, c_i):
    if node.name != 'UnaryExpression':
        logging.error("FATAL ERROR: typecheck_unary") 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: UnaryExpression has no children") 
        sys.exit(1) 

    elif node[0].name == "NotOperator":
        t = typecheck_expr(node[1], c, class_env, return_type, t_i, c_i)
        if t != "Bool":
            #logging.error("typecheck failed:", node)
            #sys.exit(42)
            pass
        else:
            logging.warning("typecheck passed", node)
            pass
        return t

    elif node[0].name == "CastExpression":
        pass

    elif node[0].name == "SubtractOperator":
        pass

    else:
        logging.warning("UnaryExpression", "has unexpected child", node[0].name) 
        sys.exit(1) 

def typecheck_add(node, c, class_env, return_type, t_i, c_i):
    expected_node = 'AdditiveExpression'
    if node.name != expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: %s has no children" % expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        return typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)

    elif node[1].name == 'AddOperator' or node[1].name == 'SubtractOperator':
        t1 = typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)
        t2 = typecheck_expr(node[2], c, class_env, return_type, t_i, c_i)
        if node[1].name == 'AddOperator' \
        and (t1 == "java.lang.String" or t2 == "java.lang.String"):
            if t1 != "Void" and t2 != "Void":
                return "java.lang.String"
            else:
                logging.error("typecheck failed: string add void")
                sys.exit(42)
        elif isNumType(t1) and isNumType(t2):
            return "Int"
        else:
            logging.error("typecheck failed: add/sub not num")
            sys.exit(42)

    else:
        logging.warning(expected_node, "has unexpected children", node.children) 
        sys.exit(1) 

def typecheck_mult(node, c, class_env, return_type, t_i, c_i):
    expected_node = 'MultiplicativeExpression'
    if node.name != expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: %s has no children" % expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        return typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)

    elif node[1].name == 'MultiplyOperator' \
    or node[1].name == 'DivideOperator' \
    or node[1].name == 'ModuloOperator':
        t1 = typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)
        t2 = typecheck_expr(node[2], c, class_env, return_type, t_i, c_i)
        if isNumType(t1) and isNumType(t2):
            return "Int"
        else:
            print(c)
            print(node.children)
            print(t1, t2)
            logging.error("typecheck failed: mult/div/mod not num")
            sys.exit(42)

    else:
        logging.warning(expected_node, "has unexpected children", node.children) 
        sys.exit(1) 

# Statements

def typecheck_return(node, c, class_env, return_type, t_i, c_i):
    if node.name != 'ReturnStatement' or return_type == None:
        logging.error("FATAL ERROR: typecheck_return") 
        sys.exit(1)
    
    t = None
    if len(node.children) == 0:
        t = "Void"
    else:
        t = typecheck_expr(node.children[0], c, class_env, return_type, t_i, c_i)
    
    if t != return_type:
        #logging.error("typecheck failed:", node)
        #sys.exit(42)
        pass
    else:
        #logging.warning("typecheck passed", node)
        pass

    return t

