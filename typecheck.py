import sys
import name_resolve
from utils import logging
from utils import node
from utils import primitives
from utils import class_hierarchy
import utils.ast

# Note: I'm going to call some statements expressions cause why not?
# ie. ReturnStatement

# gets a list of all nodes that need to be type checked
def get_exprs_from_node(n):
    exprs = []
    
    # pimary "exprs"
    exprs.extend(n.select(['Literal']))
    exprs.extend(n.select(['This']))
    exprs.extend(n.select(['FieldAccess']))
    exprs.extend(n.select(['ArrayAccess']))

    # exprs
    exprs.extend(utils.ast.get_exprs(n))

    # statement "exprs"
    exprs.extend(n.select(['ReturnStatement']))
    exprs.extend(n.select(['IfStatement']))
    exprs.extend(n.select(['WhileStatement']))
    exprs.extend(n.select(['ForStatement']))
    exprs.extend(n.select(['LocalVariableDeclaration']))
    exprs.extend(n.select(['FieldDeclaration']))
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

    # Run typecheck on each field
    for field_node in env['ClassDeclaration'].names.values():
        exprs = get_exprs_from_node(field_node)
        for expr in exprs:
            typecheck_expr(expr, c, None, t_i, c_i)

    # Run typecheck on each method
    for method_env in env['ClassDeclaration'].children:
        n = method_env.node
        m = n.obj
        exprs = get_exprs_from_node(n)
        for expr in exprs:
            is_static = 'Static' in m.mods
            typecheck_expr(expr, c, m, t_i, c_i)

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

def typecheck_expr(node, c, method, t_i, c_i):
    # see if type for expr has already been resolved
    if hasattr(node, 'typ') and node.typ != None:
        return node.typ
    
    t = None

    # DO STUFF HERE...
    if node.name == 'Assignment':
        t = typecheck_assignment(node, c, method, t_i, c_i)
    elif node.name == 'MethodInvocation':
        t = typecheck_method_invocation(node, c, method, t_i, c_i)
    elif node.name == 'CreationExpression':
        t = typecheck_creation(node, c, method, t_i, c_i)
    elif node.name == 'ConditionalOrExpression' \
    or node.name == 'ConditionalAndExpression':
        t = typecheck_conditional(node, c, method, t_i, c_i)
    elif node.name == 'EqualityExpression':
        t = typecheck_equality(node, c, method, t_i, c_i)
    elif node.name == 'RelationalExpression':
        t = typecheck_relational(node, c, method, t_i, c_i)
    elif node.name == 'AdditiveExpression':
        t = typecheck_add(node, c, method, t_i, c_i)
    elif node.name == 'MultiplicativeExpression':
        t = typecheck_mult(node, c, method, t_i, c_i)
    elif node.name == 'UnaryExpression':
        t = typecheck_unary(node, c, method, t_i, c_i)
    elif node.name == 'PostfixExpression':
        t = typecheck_postfix(node, c, method, t_i, c_i)
    elif node.name == 'CastExpression':
        t = typecheck_cast_expression(node, c, method, t_i, c_i)
    elif node.name == 'InstanceofExpression':
        t = typecheck_instanceof(node, c, method, t_i, c_i)
    elif node.name == 'AndExpression' or node.name == 'InclusiveOrExpression':
        t = typecheck_eager_boolean(node, c, method, t_i, c_i)

    # Statements
    elif node.name == 'ReturnStatement':
        t = typecheck_return(node, c, method, t_i, c_i)
    elif node.name == 'IfStatement':
        t = typecheck_if(node, c, method, t_i, c_i)
    elif node.name == 'WhileStatement':
        t = typecheck_while(node, c, method, t_i, c_i)
    elif node.name == 'ForStatement':
        t = typecheck_for(node, c, method, t_i, c_i)
    elif node.name == 'LocalVariableDeclaration' or node.name == 'FieldDeclaration':
        t = typecheck_local_var_decl(node, c, method, t_i, c_i)

    # Primarys
    elif node.name == 'Literal':
        t = typecheck_literal(node, c, method, t_i, c_i)
    elif node.name == 'This':
        t = c.name
    elif node.name == 'FieldAccess':
        t = typecheck_field_access(node, c, method, t_i, c_i)
    elif node.name == 'ArrayAccess':
        t = typecheck_array_access(node, c, method, t_i, c_i)

    elif node.name == 'ExclusiveOrExpression':
        logging.error("SHOULD NOT SEE THESE")
        sys.exit(1)
    else:
        logging.warning("typecheck could not run on " + node.name)

    if not isinstance(t, str) and t != None:
        logging.warning("typecheck found a non-type", node.name, t)

    # set type
    node.typ = t

    # return the type
    return t

###############################################################################

def typecheck_assignment(node, c, method, t_i, c_i):
    lhs_type = None
    if node[0].name == 'Name':
        lhs_type = typecheck_name(node[0])

        # Special case: Cannot assign to the "length" field of an array.
        if node[0].decl.name == 'FakeFieldDeclaration':
            logging.error('Cannot assign to length field of array')
            sys.exit(42)

    # Make sure that 
    elif node[0].name == 'FieldAccess':
        lhs_type = typecheck_field_access(node[0], c, method,
            t_i, c_i)
        """
        # Special case: Cannot assign to the "length" field of an array.
        field_name = node[0][0][0].value.value

        # Check if field_receiver is an array type.
        field_receiver_expr = node[0][1][0]
        field_receiver_typ = typecheck_expr(field_receiver_expr, c,
            method, t_i, c_i)
        if is_array_type(field_receiver_typ) and field_name == length:
            logging.error('Cannot assign to length field of array')
            sys.exit(42)
        """
        
    elif node[0].name == 'ArrayAccess':
        lhs_type = typecheck_array_access(node[0], c, method,
            t_i, c_i)
    else:
        logging.error('FATAL ERROR: Invalid typecheck_assignment')
        sys.exit(1) # should not happen

    rhs_type = typecheck_expr(node[1], c, method, t_i, c_i)
    
    if is_assignable(lhs_type, rhs_type, c_i):
        node.typ = lhs_type
        return node.typ
    else:
        logging.error('Cannot assign expression of type %s to LHS of type %s' %
            (rhs_type, lhs_type))
        sys.exit(42)

# Note: static field accesses are always ambiguous, and are handled elsewhere.
# (Field Accesses that can be name resolved are converted to Name nodes)
def typecheck_field_access(node, c, method, t_i, c_i):
    if node.name != 'FieldAccess':
        logging.error('FATAL ERROR: invalid node %s for field access' %
            node.name)
        sys.exit(1)

    receiver_type = typecheck_expr(node[1][0], c, method, t_i,
        c_i)
    
    field_name = node[0][0].value.value

    if receiver_type == None:
        logging.warning("FATAL: FieldAccess")
        return

    if is_array_type(receiver_type):
        if field_name == 'length':
            node.typ = 'Int'
            return 'Int'
        else:
            logging.error('Invalid field access on array type %s' %
                receiver_type)
            sys.exit(42)
    elif primitives.is_primitive(receiver_type) == True:
        logging.error('Invalid field access on primitive type %s' %
            receiver_type)
    else:
        field_decl = name_resolve.field_accessable(c_i, t_i, receiver_type,
            field_name, c.name, False)

        if field_decl is None:
            logging.error('Cannot access field %s of type %s from class %s' %
                (field_name, receiver_type, c.name))
            sys.exit(42)
        elif 'Static' in field_decl.obj.mods:
            logging.error('Instance field method on non-static field')
            sys.exit(42)
        else:
            node.typ = field_decl[1].canon
            return node.typ

def typecheck_array_access(node, c, method, t_i, c_i):
    if node.name != 'ArrayAccess':
        logging.error('FATAL ERROR: invalid node %s for array access' %
            node.name)
        sys.exit(1)

    receiver_type = None
    if node[0][0].name == 'Name':
        receiver_type = typecheck_name(node[0][0])
    else:
        receiver_type = typecheck_expr(node[0][0], c, method,
            t_i, c_i)

    # Must be array type.
    if not is_array_type(receiver_type):
        logging.error('Cannot index into non-array type')
        sys.exit(42)

    # Expression must be a number.
    expr_type = typecheck_expr(node[1], c, method, t_i, c_i)
    
    if not primitives.is_numeric(expr_type):
        logging.error('Array access with non-numeric type %s' % expr_type)
        sys.exit(42)

    node.typ = get_arraytype(receiver_type)
    return node.typ

def typecheck_method_invocation(node, c, method, t_i, c_i):
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
        receiver_type = typecheck_expr(node[1][0], c, method,
            t_i, c_i)

    if primitives.is_primitive(receiver_type):
        logging.error('Cannot call method on primitive type %s' % receiver_type)
        sys.exit(42)
    if is_array_type(receiver_type):
        logging.error('Cannot call method on array type %s' % receiver_type)
        sys.exit(42)

    # Build types of arguments.
    arg_canon_types = []
    for argument_expr in node[2].children:
        arg_canon_types.append(typecheck_expr(argument_expr, c,
            method, t_i, c_i))

    # Call helper to find a method with the given signature (name and args).
    method_decl = name_resolve.method_accessable(c_i, t_i,
        receiver_type, method_name, arg_canon_types, c.name, not is_static)
    if method_decl == None:
        logging.error('Invalid method invocation')
        logging.error(" ", method_decl, receiver_type, method_name, arg_canon_types)
        sys.exit(42)
    if method_decl.name != 'MethodDeclaration':
        logging.error('Did not find method declaration')
        sys.exit(42)
        
    if 'Static' in method_decl.obj.mods and is_static == False:
        logging.error('Invalid static method invocation')
        sys.exit(42)
    elif 'Static' not in method_decl.obj.mods and is_static == True:
        logging.error('Invalid instance method invocation (of static method)')
        sys.exit(42)

    # Check for implicit This reference in static method
    if len(node[1].children) == 0 \
    and 'Static' in method.mods and 'Static' not in method_decl.obj.mods:
        logging.error('Nonstatic access in a static method', method.name)
        sys.exit(42)

    # Link the invocation of the method with its declaration
    node.decl = method_decl

    # Get the return type of the method.
    node.typ = method_decl.obj.type

    return node.typ

def typecheck_cast_expression(node, c, method, t_i, c_i):
    if node.name != 'CastExpression':
        logging.error('FATAL: Invalid node %s for typecheck_cast_expression' %
            node.name)
        sys.exit(1)

    expr_type = typecheck_expr(node[1], c, method, t_i, c_i)
    if (primitives.is_numeric(expr_type) and primitives.is_numeric(node[0].canon)) \
        or is_assignable(expr_type, node[0].canon, c_i) \
        or is_assignable(node[0].canon, expr_type, c_i):
        return node[0].canon
    else:
        logging.error('Cast expression of type %s into %s' %
            (expr_type, node[0].canon))
        sys.exit(42)

def typecheck_literal(node, c, method, t_i, c_i):
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

def typecheck_postfix(node, c, method, t_i, c_i):
    expected_node = 'PostfixExpression'
    if node.name != expected_node:
        logging.error("FATAL ERROR: typecheck_postfix() got", node.name)
        sys.exit(1)

    if len(node.children) == 0:
        logging.error("FATAL ERROR")
        sys.exit(1)

    if node[0].name == 'Name':
        node.typ = typecheck_name(node[0])
    else:
        node.typ = typecheck_expr(node[0], c, method, t_i, c_i)

    return node.typ

# Operators

def typecheck_unary(node, c, method, t_i, c_i):
    if node.name != 'UnaryExpression':
        logging.error("FATAL ERROR: typecheck_unary") 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: UnaryExpression has no children") 
        sys.exit(1) 

    elif node[0].name == "NotOperator":
        t = typecheck_expr(node[1], c, method, t_i, c_i)
        if t != "Boolean":
            logging.error("typecheck failed: NotOp expects boolean; got:",t)
            sys.exit(42)

        return t

    elif node[0].name == "CastExpression":
        return typecheck_expr(node[0], c, method, t_i, c_i)

    elif node[0].name == "SubtractOperator":
        t = typecheck_expr(node[1], c, method, t_i, c_i)
        if not primitives.is_numeric(t):
            logging.error("typecheck failed: SubtractOp expects number; got:",t)
            sys.exit(42)
        return t

    else:
        logging.warning("UnaryExpression", "has unexpected child", node[0].name) 
        sys.exit(1) 

def typecheck_conditional(node, c, method, t_i, c_i):
    expected_node = ['ConditionalAndExpression', 'ConditionalOrExpression']
    if node.name not in expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: has no children", expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        return typecheck_expr(node[0], c, method, t_i, c_i)

    elif node[1].name == 'AndOperator' \
    or node[1].name == 'OrOperator':
        t1 = typecheck_expr(node[0], c, method, t_i, c_i)
        t2 = typecheck_expr(node[2], c, method, t_i, c_i)
        if t1 == 'Boolean' and t2 == 'Boolean':
            return 'Boolean'
        else:
            logging.error("typecheck failed: expected booleans; got:", t1, t2)
            sys.exit(42)

    else:
        logging.warning(expected_node, "has unexpected children", node.children) 
        sys.exit(1) 

def typecheck_equality(node, c, method, t_i, c_i):
    expected_node = ['EqualityExpression']
    if node.name not in expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: has no children", expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        return typecheck_expr(node[0], c, method, t_i, c_i)

    elif node[1].name == 'EqualOperator' \
    or node[1].name == 'NotEqualOperator':
        t1 = typecheck_expr(node[0], c, method, t_i, c_i)
        t2 = typecheck_expr(node[2], c, method, t_i, c_i)
        if primitives.is_numeric(t1) and primitives.is_numeric(t2):
            return "Boolean"
        elif t1 == "Boolean" and t2 == "Boolean":
            return "Boolean"
        elif is_assignable(t1, t2, c_i) or is_assignable(t2, t1, c_i): 
            return "Boolean"
        else:
            logging.error("typecheck failed: equality between", t1, t2)
            sys.exit(42)

    else:
        logging.warning(expected_node, "has unexpected children", node.children) 
        sys.exit(1) 

def typecheck_relational(node, c, method, t_i, c_i):
    expected_node = ['RelationalExpression']
    if node.name not in expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: has no children", expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        return typecheck_expr(node[0], c, method, t_i, c_i)

    elif node[1].name == 'LessThanOperator' \
    or node[1].name == 'GreaterThanOperator' \
    or node[1].name == 'LessThanEqualOperator' \
    or node[1].name == 'GreaterThanEqualOperator':
        t1 = typecheck_expr(node[0], c, method, t_i, c_i)
        t2 = typecheck_expr(node[2], c, method, t_i, c_i)
        if primitives.is_numeric(t1) and primitives.is_numeric(t2):
            return "Boolean"
        else:
            logging.error("typecheck failed: Relational:", t1, t2)
            sys.exit(42)

    else:
        logging.warning(expected_node, "has unexpected children", node.children) 
        sys.exit(1) 

def typecheck_add(node, c, method, t_i, c_i):
    expected_node = 'AdditiveExpression'
    if node.name != expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: %s has no children" % expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        return typecheck_expr(node[0], c, method, t_i, c_i)

    elif node[1].name == 'AddOperator' or node[1].name == 'SubtractOperator':
        t1 = typecheck_expr(node[0], c, method, t_i, c_i)
        t2 = typecheck_expr(node[2], c, method, t_i, c_i)
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
            logging.error("typecheck failed: Add:", t1, t2)
            sys.exit(42)

    else:
        logging.warning(expected_node, "has unexpected children", node.children) 
        sys.exit(1) 

def typecheck_mult(node, c, method, t_i, c_i):
    expected_node = 'MultiplicativeExpression'
    if node.name != expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)
    
    if len(node.children) == 0:
        logging.error("FATAL ERROR: %s has no children in typecheck_mult()" %
            expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        logging.error('FATAL ERROR: Got only one child in binary expression')
        sys.exit(1)

    elif node[1].name == 'MultiplyOperator' \
    or node[1].name == 'DivideOperator' \
    or node[1].name == 'ModuloOperator':
        t1 = typecheck_expr(node[0], c, method, t_i, c_i)
        t2 = typecheck_expr(node[2], c, method, t_i, c_i)
        if primitives.is_numeric(t1) and primitives.is_numeric(t2):
            return "Int"
        else:
            logging.error("typecheck failed: mult/div/mod not num")
            sys.exit(42)

    else:
        logging.warning(expected_node, "has unexpected children", node.children) 
        sys.exit(1) 

def typecheck_creation(node, c, method, t_i, c_i):
    expected_node = 'CreationExpression'
    if node.name != expected_node:
        logging.error("FATAL ERROR: expected", expected_node) 
        sys.exit(1)

    creation_type = node[0].canon
    if is_array_type(creation_type):
        if len(node[1].children) > 1:
            logging.error('Too many args to array creation')
            sys.exit(42)
        if len(node[1].children) == 1:
            expr_type = typecheck_expr(node[1][0], c,
                method, t_i, c_i)
            if not primitives.is_numeric(expr_type):
                logging.error('Invalid array creation argument')
                sys.exit(42)
        node.typ = creation_type
        return node.typ

    else:
        cons_name = creation_type.split('.')[-1]

        # Check that we don't call constructor of an abstract class.
        if 'Abstract' in c_i[creation_type].mods:
            logging.error('Cannot call constructor of abstract class')
            sys.exit(42)
        
        arg_types = []
        for arg_expr in node[1].children:
            arg_types.append(typecheck_expr(arg_expr, c, method,
                t_i, c_i))

        cons_decl = name_resolve.constructor_accessable(c_i, t_i,
            creation_type, cons_name, arg_types, c.name, False)

        cons = class_hierarchy.Temp_Constructor(cons_name, arg_types)
        # TODO: Check that cons is not protected, and if it is, we have access
        # to call it.
        if cons_decl != None and cons in c_i[creation_type].declare:
            node.typ = creation_type
            return node.typ
        else:
            logging.error('Invalid constructor call')
            sys.exit(42)

def typecheck_instanceof(node, c, method, t_i, c_i):
    expected_node = 'InstanceofExpression'
    if node.name != expected_node:
        logging.error('FATAL ERROR: expected', expected_node)
        sys.exit(1)

    lhs_type = typecheck_expr(node[0], c, method, t_i, c_i)
    rhs_type = node[2].canon

    if primitives.is_primitive(rhs_type):
        logging.error('Invalid Instanceof type %s' % rhs_type)
        sys.exit(42)
    
    if is_assignable(lhs_type, rhs_type, c_i) or \
            is_assignable(rhs_type, lhs_type, c_i):
        node.typ = 'Boolean'
        return node.typ
    else:
        logging.error('Invalid %s instanceof %s' % (lhs_type, rhs_type))
        sys.exit(42)

def typecheck_eager_boolean(node, c, method, t_i, c_i):
    if node.name not in ['AndExpression', 'InclusiveOrExpression']:
        logging.error('FATAL ERROR: Incorrect node %s passed to typecheck_eager_boolean()' %
            node.name)
        sys.exit(1)

    if len(node.children) == 0:
        logging.error("FATAL ERROR: %s has no children in typecheck_mult()" %
            expected_node) 
        sys.exit(1) 

    elif len(node.children) == 1:
        logging.error('FATAL ERROR: Got only one child in binary expression')
        sys.exit(1)

    t1 = typecheck_expr(node[0], c, method, t_i, c_i)
    t2 = typecheck_expr(node[2], c, method, t_i, c_i)

    if t1 != 'Boolean' or t2 != 'Boolean':
        logging.error('Operators & and | only valid on boolean operands')
        sys.exit(1)
    else:
        node.typ = 'Boolean'
        return node.typ

# Statements

def typecheck_return(node, c, method, t_i, c_i):
    if node.name != 'ReturnStatement' or method == None:
        logging.error("FATAL ERROR: typecheck_return") 
        sys.exit(1)
    
    t = None
    if len(node.children) == 0:
        t = "Void"
    else:
        t = typecheck_expr(node.children[0], c, method, t_i, c_i)

        if t == 'Void':
            logging.error("typecheck failed: Return: got Void return type")
            sys.exit(42)

    expected_type = method.type
    if expected_type == None:
        expected_type = 'Void'
    if t != expected_type and not is_assignable(expected_type, t, c_i):
        logging.error("typecheck failed: Return: expected %s but got %s" % (expected_type, t))
        sys.exit(42)

    return None

def typecheck_if(node, c, method, t_i, c_i):
    if node.name != 'IfStatement':
        logging.error('FATAL ERROR: typecheck_if')
        sys.exit(1)

    expr_type = typecheck_expr(node[0], c, method, t_i, c_i)

    if expr_type != 'Boolean':
        logging.error('Type of expression for if must be a Boolean')
        sys.exit(42)

    return None

def typecheck_while(node, c, method, t_i, c_i):
    if node.name != 'WhileStatement':
        logging.error('FATAL ERROR: typecheck_while')
        sys.exit(1)

    expr_type = typecheck_expr(node[0], c, method, t_i, c_i)

    if expr_type != 'Boolean':
        logging.error('Type of expression for \'while\' must be a Boolean')
        sys.exit(42)
    
    return None

def typecheck_for(node, c, method, t_i, c_i):
    if node.name != 'ForStatement':
        logging.error('FATAL ERROR: typecheck_for')
        sys.exit(1)

    # If there's no 'ForCondition', don't need to do anything.
    if len(node[1].children) == 0:
        return None
    else:
        expr_type = typecheck_expr(node[1][0], c, method, t_i,
            c_i)

        if expr_type != 'Boolean':
            logging.error('Type of expression for \'for\' must be a Boolean')
            sys.exit(42)
        
        return None

def typecheck_local_var_decl(node, c, method, t_i, c_i):
    type_node = node.find_child('Type')
    init_node = node.find_child('Initializer')

    if type_node == None or init_node == None:
        logging.error('FATAL ERROR: typecheck_var_decl')
        sys.exit(1)

    # Extract type from Type node.
    var_type = type_node.canon
    initializer_type = var_type

    if len(init_node.children) == 1:
        initializer_type = typecheck_expr(init_node[0], c, method, t_i, c_i)

    if is_assignable(var_type, initializer_type, c_i):
        node.typ = var_type
        return node.typ
    else:
        logging.error('Invalid initializer for variable of type %s to %s' % (initializer_type, var_type))
        sys.exit(42)

# type1 is lhs (to be assigned), type2 is rhs (value to assign)
def is_assignable(type1, type2, c_i):
    # Call other helper for anything having to do with arrays.
    if is_array_type(type1) or is_array_type(type2):
        return is_array_assignable(type1, type2, c_i)

    if type1 in ['Void', 'Null'] or type2 == 'Void':
        return False
    elif type1 == type2:
        return True
    elif primitives.is_reference(type1) and type2 == 'Null':
        return True
    elif primitives.is_numeric(type1) and primitives.is_numeric(type2):
        return primitives.is_widening_conversion(type1, type2)
    elif primitives.is_reference(type1) and primitives.is_reference(type2):
        return is_nonstrict_subclass(type1, type2, c_i)
    else:
        return False

def is_array_assignable(type1, type2, c_i):
    if is_array_type(type1) and type2 == 'Null':
        return True
    elif is_array_type(type1) and not is_array_type(type2):
        return False

    if type1 == 'java.lang.Object' and is_array_type(type2):
        return True
    elif type1 == 'java.lang.Cloneable' and is_array_type(type2):
        return True
    elif type1 == 'java.io.Serializable' and is_array_type(type2):
        return True
    elif is_array_type(type1) and is_array_type(type2):
        atyp1 = get_arraytype(type1)
        atyp2 = get_arraytype(type2)
        if atyp1 == atyp2:
            return True
        # Unequal primitive types.
        elif primitives.is_primitive(atyp1) and primitives.is_primitive(atyp2):
            return False
        else:
            return is_nonstrict_subclass(atyp1, atyp2, c_i)
    else:
        return False

# Returns True if type1 and type2 refer to the same class, or type
def is_nonstrict_subclass(type1, type2, c_i):
    if type1 == None or type2 == None:
        return False

    # everything is always a subclass of Object (must be special case for interfaces)
    if type1 == 'java.lang.Object':
        return True

    # Starting at type2, do a search up class hierarchy for type1
    queue = [type2]
    while len(queue) > 0:
        typename = queue.pop(0)

        # Found type1 as a superclass of type1.
        if type1 == typename:
            return True
        else:
            cls = c_i[typename]
            queue.extend([x.name for x in cls.implements])
            if cls.extends != None:
                queue.append(cls.extends.name)

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

