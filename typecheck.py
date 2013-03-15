import sys
import name_resolve
from utils import logging
from utils import node
from utils import primitives

# Note: I'm going to call some statements expressions cause why not?
# ie. ReturnStatement

# gets a list of all nodes that need to be type checked
def get_exprs_from_node(n):
    exprs = []
    
    # pimary "exprs"
    exprs.extend(n.select(['Literal']))
    exprs.extend(n.select(['This']))
    exprs.extend(n.select(['FieldAccess']))
    exprs.extend(n.select(['MethodInvocation']))
    exprs.extend(n.select(['ArrayAccess']))


    # exprs
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

def typecheck(t_i, c_i):
    for type_name, env in t_i.items():
        c = c_i[type_name]
        typecheck_methods(c, env, t_i, c_i)

def typecheck_methods(c, env, t_i, c_i):
    # interface has typecheck on field inits
    if c.interface:
        # TODO
        return

    #print("  #", c)
    # Run typecheck on each field
    for field_node in env['ClassDeclaration'].names.values():
        #print("    !", field_node)
        exprs = get_exprs_from_node(field_node)
        for expr in exprs:
            typecheck_expr(expr, c, env, None, t_i, c_i)

    # Run typecheck on each method
    for method_env in env['ClassDeclaration'].children:
        #print("    @", method_env)
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
###############################################################################

# Get the type from the input name node.
def typecheck_name(node):
    return node.typ

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
    elif node.name == 'ConditionalOrExpression' \
    or node.name == 'ConditionalAndExpression':
        t = typecheck_conditional(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'EqualityExpression':
        t = typecheck_equality(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'RelationalExpression':
        t = typecheck_relational(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'AdditiveExpression':
        t = typecheck_add(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'MultiplicativeExpression':
        t = typecheck_mult(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'UnaryExpression':
        t = typecheck_unary(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'PostfixExpression':
        if len(node.children) == 0:
            logging.error("FATAL ERROR")
            sys.exit(1)
        if node[0].name == 'Name':
            t = typecheck_name(node[0])
        else:
            t = typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)
    elif node.name == 'CastExpression':
        t = typecheck_cast_expression(node, c, class_env, return_type, t_i, c_i)

    # Statements
    elif node.name == 'ReturnStatement':
        t = typecheck_return(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'IfStatement' \
    or   node.name == 'WhileStatement':
        pass
    elif node.name == 'ForStatement':
        pass

    # Primarys
    elif node.name == 'Literal':
        t = typecheck_literal(node, c, class_env, return_type, t_i, c_i)
    elif node.name == 'This':
        t = c.name

    elif node.name == 'InclusiveOrExpression' \
        or   node.name == 'ExclusiveOrExpression' \
        or   node.name == 'AndExpression':
        logging.error("SHOULD NOT SEE THESE")
        sys.exit(1)
    else:
        pass

    if not isinstance(t, str) and t != None:
        logging.warning("typecheck found a non-type", node.name, t)

    # set type
    node.typ = t

    # return the type
    return t

###############################################################################

def typecheck_assignment(node, c, class_env, return_type, t_i, c_i):
    lhs_type = None
    if node[0].name == 'Name':
        lhs_type == typecheck_name(node[0]) # TODO
    elif node[0].name == 'FieldAccess':
        lhs_type == typecheck_field_access(node[0], c, class_env, return_type,
            t_i, c_i)
        # Special case: Cannot assign to the "length" field of an array.
        field_receiver == field_access
    elif node[0].name == 'ArrayAccess':
        lhs_type == typecheck_array_access(node[0], c, class_env, return_type,
            t_i, c_i)
    else:
        logging.error('FATAL ERROR: Invalid typecheck_assignment')
        sys.exit(1) # should not happen

    rhs_type = typecheck_expr(node[1])
    
    if is_assignable(lhs_type, rhs_type, c_i):
        node.typ = lhs_type
    else:
        logging.error('Cannot assign expression of type %s to LHS of type %s' %
            (rhs_type, lhs_type))
        sys.exit(42)
    return node.typ

# Note: static field accesses are always ambiguous, and are handled elsewhere.
def typecheck_field_access(node, c, class_env, return_type, t_i, c_i):
    if node.name != 'FieldAccess':
        logging.error('FATAL ERROR: invalid node %s for field access' %
            node.name)
        sys.exit(1)

    receiver_type = typecheck_expr(node[1][0], c, class_env, return_type, t_i,
        c_i)
    field_name = node[0][0].value.value
    if is_array_type(receiver_type):
        if field_name == 'length':
            node.typ = 'Int'
            return 'Int'
        else:
            logging.error('Invalid field access on array type %s' %
                receiver_type)
            sys.exit(42)
    elif primitive.is_primitive(receiver_type) == True:
        logging.error('Invalid field access on primitive type %s' %
            receiver_type)
    else:
        field_type = name_resolve.accessible_field(c_i, t_i, receiver_type,
            field_name, c.name)
        if field_type is None:
            logging.error('Cannot access field %s of type %s from class %s' %
                (field_name, receiver_type, c.name))
            sys.exit(42)
        else:
            node.typ = field_type
            return field_type

def typecheck_array_access(node, c, class_env, return_type, t_i, c_i):
    if node.name != 'ArrayAccess':
        logging.error('FATAL ERROR: invalid node %s for array access' %
            node.name)
        sys.exit(1)

    receiver_type = None
    if node[0][0].name == 'Name':
        receiver_type = typecheck_name(node[0][0])
    else:
        receiver_type = typecheck_expr(node[0][0], c, class_env, return_type,
            t_i, c_i)

    # Must be array type.
    if not is_array_type(receiver_type):
        logging.error('Cannot index into non-array type')
        sys.exit(42)

    # Expression must be a number.
    expr_type = typecheck_expr(node[1], c, class_env, return_type, t_i, c_i)
    if not primary.is_numeric(expr_type):
        logging.error('Array access with non-numeric type %s' % expr_type)
        sys.exit(42)

    node.typ = get_arraytype(receiver_type)
    return node.typ

def typecheck_method_invocation(node, c, class_env, return_type, t_i, c_i):
    if node.name != 'MethodInvocation':
        logging.error('FATAL ERROR: invalid node %s for method invocation' %
            node.name)
        sys.exit(1)

    method_name = node[0][0].value.value

    # Get the type of whatever we're calling the method on.
    receiver_type = None
    is_static = False
    if len(node[1].children) == 0:
        receiver_type = c.name
    elif node[1][0].name == 'Name':
        if node[1][0].canon == None:
            receiver_type = typecheck_name(node[1][0])
        else:
            receiver_type = node[1][0].canon
            is_static = True
    else: # Primary
        receiver_type = typecheck_expr(node[1][0])

    # Build types of arguments.
    arg_canon_types = []
    for argument_expr in node[2].children:
        arg_canon_types.append(typecheck_expr(argument_expr))

    # Call helper to find a method with the given signature (name and args).
    method_decl = name_resolve.accessible_method(c_i, t_i,
        receiver_type, method_name, c.name, arg_canon_types)
    if method_decl == None:
        logging.error('Invalid method invocation')
        sys.exit(42)
        
    if 'static' in method_decl.modifiers and is_static == False:
        logging.error('Invalid static method invocation')
        sys.exit(42)
    elif 'static' not in method_decl.modifier and is_static == True:
        logging.error('Invalid instance method invocation (of static method)')
        sys.exit(42)

    # Get the return type of the method.
    if method_decl[1].name == 'Void':
        node.typ = 'Void'
    else:
        node.typ = method_decl[1].canon

    return node.typ

def typecheck_cast_expression(node, c, class_env, return_type, t_i, c_i):
    if node.name != 'CastExpression':
        logging.error('FATAL: Invalid node %s for typecheck_cast_expression' %
            node.name)
        sys.exit(1)

    expr_type = typecheck_expr(node[1], c, class_env, return_type, t_i, c_i)
    if is_assignable(expr_type, node[0].canon, c_i) \
    or is_assignable(node[0].canon, expr_type, c_i):
        return node[0].canon
    else:
        logging.error('Cast expression of type %s into %s' %
            (expr_type, node[0].canon))
        #sys.exit(42)

def typecheck_literal(node, c, class_env, return_type, t_i, c_i):
    if node.name != 'Literal':
        logging.error('FATAL ERROR: Invalid node %s for typecheck_literal' %
            node.name)
        sys.exit(1)
    
    # Check children to determine type.
    if node[0].name == 'DecimalIntegerLiteral':
        node.typ = 'Int'
    elif node[0].name == 'BooleanLiteral':
        node.typ = 'Boolean'
    elif node[0].name == 'CharacterLiteral':
        node.typ = 'Char'
    elif node[0].name == 'StringLiteral':
        node.typ = 'java.lang.String'
    elif node[0].name == 'NullLiteral':
        node.typ = 'Null'

    if node.typ == None:
        logging.error("FATAL ERROR?: Could not resolve literal.")
        sys.exit(1) # Could not resolve type, compiler error?

    return node.typ

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
        if t != "Boolean":
            logging.error("typecheck failed:", node)
            #sys.exit(42)
        return t

    elif node[0].name == "CastExpression":
        return typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)

    elif node[0].name == "SubtractOperator":
        t = typecheck_expr(node[1], c, class_env, return_type, t_i, c_i)
        if primitives.is_numeric(t):
            logging.error("typecheck failed:", node)
            #sys.exit(42)
        return t

    else:
        logging.warning("UnaryExpression", "has unexpected child", node[0].name) 
        sys.exit(1) 

def typecheck_conditional(node, c, class_env, return_type, t_i, c_i):
    expected_node = ['ConditionalAndExpression', 'ConditionalOrExpression']
    if node.name not in expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: has no children", expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        return typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)

    elif node[1].name == 'AndOperator' \
    or node[1].name == 'OrOperator':
        t1 = typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)
        t2 = typecheck_expr(node[2], c, class_env, return_type, t_i, c_i)
        if primitives.is_numeric(t1) and primitives.is_numeric(t2):
            return "Boolean"
        else:
            logging.error("typecheck failed: and/or not bool")
            #sys.exit(42)

    else:
        logging.warning(expected_node, "has unexpected children", node.children) 
        sys.exit(1) 

def typecheck_equality(node, c, class_env, return_type, t_i, c_i):
    expected_node = ['EqualityExpression']
    if node.name not in expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: has no children", expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        return typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)

    elif node[1].name == 'EqualOperator' \
    or node[1].name == 'NotEqualOperator':
        t1 = typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)
        t2 = typecheck_expr(node[2], c, class_env, return_type, t_i, c_i)
        if primitives.is_numeric(t1) and primitives.is_numeric(t2):
            return "Boolean"
        elif t1 == "Boolean" and t2 == "Boolean":
            return "Boolean"
        elif (t1 == "Null" or primitives.is_reference(t1)) \
        and  (t2 == "Null" or primitives.is_reference(t2)):
            return "Boolean"
        else:
            logging.error("typecheck failed", expected_node)
            #sys.exit(42)

    else:
        logging.warning(expected_node, "has unexpected children", node.children) 
        sys.exit(1) 

def typecheck_relational(node, c, class_env, return_type, t_i, c_i):
    expected_node = ['RelationalExpression']
    if node.name not in expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: has no children", expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        return typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)

    elif node[1].name == 'LessThanOperator' \
    or node[1].name == 'GreaterThanOperator' \
    or node[1].name == 'LessThanEqualOperator' \
    or node[1].name == 'GreaterThanEqualOperator':
        t1 = typecheck_expr(node[0], c, class_env, return_type, t_i, c_i)
        t2 = typecheck_expr(node[2], c, class_env, return_type, t_i, c_i)
        if primitives.is_numeric(t1) and primitives.is_numeric(t2):
            return "Boolean"
        else:
            logging.error("typecheck failed", expected_node)
            #sys.exit(42)

    else:
        logging.warning(expected_node, "has unexpected children", node.children) 
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
        elif primitives.is_numeric(t1) and primitives.is_numeric(t2):
            return "Int"
        else:
            logging.error("typecheck failed: add/sub not num")
            #sys.exit(42)

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
        if primitives.is_numeric(t1) and primitives.is_numeric(t2):
            return "Int"
        else:
            logging.error("typecheck failed: mult/div/mod not num")
            #sys.exit(42)

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
    
    if t == return_type \
    or (primitives.is_reference(return_type) and t == "Null"):
        #logging.warning("typecheck passed", node)
        pass
    else:
        logging.error("typecheck failed: expected %s but got %s" % (return_type, t))
        #sys.exit(42)

    return None

def is_assignable(type1, type2, c_i):
    # Call other helper for anything having to do with arrays.
    if is_array_type(type1) or is_array_type(type2):
        return is_array_assignable(type1, type2, c_i)

    if type1 == type2:
        return True
    elif primitives.is_reference(type1) and type2 == 'Null':
        return True
    elif primitives.is_numeric(type1) and primitives.is_numeric(type2):
        return primitives.is_widening_conversion(type1, type2)
    elif not primitives.is_primitive(type1) and primitives.is_primitive(type2):
        return is_nonstrict_subclass(type2, type1, c_i)
    else:
        return False

def is_array_assignable(type1, type2, c_i):
    if type1 == 'java.lang.Object' and is_array_type(type2):
        return True
    elif type1 == 'java.lang.Cloneable' and is_array_type(type2):
        return True
    elif type1 == 'java.lang.Serializable' and is_array_type(type2):
        return True
    elif is_array_type(type1) and is_array_type(type2):
        return is_assignable(get_arraytype(type1), get_arraytype(type2), c_i)

# Returns True if type1 and type2 refer to the same class, or type
def is_nonstrict_subclass(type1, type2, c_i):
    if type1 == None or type2 == None:
        return False

    # Do a BFS up the hierarchy.
    queue = [type2]
    while len(queue) > 0:
        typename = queue.pop(0)

        # Found type1 as a superclass of type2.
        if type1 == typename:
            return True
        else:
            cls = c_i[typename]
            queue.extend(list(cls.implements))
            if cls.extends != None:
                queue.append(cls.extends)

    # Did not find type1 as a superclass of type2.
    return False

def is_array_type(typ):
    return isinstance(typ, str) and typ.endswith('[]')

def get_arraytype(typ):
    if is_array_type(typ):
        return typ[:-2]
    else:
        logging.error("FATAL ERROR: non-array type %s provided to get_arraytype" %
            typ)
        sys.exit(-1)

