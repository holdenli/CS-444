# Code generation for expressions.

def gen_expr(info, node):
    if node.name == 'Assignment':
        return gen_assignment(info, node)
    elif node.name == 'PostfixExpression':
        return gen_postfix_expr(info, node)

def gen_assignment(info, node):
    output = []

    # Get the *address* of the L-value. This means we call the _addr version
    # of the method.
    if node[0].name == 'FieldAccess':
        output.extend(gen_field_access_addr(info, node[0]))
    elif node[0].name == 'ArrayAccess':
        output.extend(gen_array_access_addr(info, node[0]))
    else:
        output.extend(gen_ambiguous_name_addr(info, node[0]))

    output.append('push eax')

    output.extend(gen_expr(info, node[1]))

    output.append('pop ebx')

    # TODO: Type check if ebx (L-value) is array element.
    if node[0].name == 'ArrayAccess':
        # output.extend(typecheck_array_assign)
        pass

    output.append('mov [ebx], eax')

    # eax contains the RHS, so we're done.

    return output

def gen_postfix_expr(info, node):
   
    # literal, this, fieldaccess, methodinvoc, arrayaccess, etc..

    output = []
    if node[0].name == 'Literal':
        output.extend(gen_literal_expr(info, node[0]))

    return output

def gen_literal_expr(info, node):
    output = []
    if node[0].name == 'DecimalIntegerLiteral':
        output.append("dd %s" % node[0].value)

    elif node[0].name == 'BooleanLiteral':
        output.append("dd %s" % int(node[0].value == 'true'))

    elif node[0].name == 'CharacterLiteral':
        output.append("dd %s" % node[0].value) # .value = "'c'"

    elif node[0].name == 'StringLiteral':
        pass
    
    elif node[0].name == 'NullLiteral':
        output.append('dd 0')

    # Push value onto stack.
    output.append('push eax')

    return output

# call method
def gen_method_invocation(info, node):
    output = ["; gen_method_invocation for %s" % node.decl.label]

    # get addr of method receiver
    obj_output = gen_expr(info, node.find_child("MethodReceiver"))
    output.extend(obj_output)
    util.null_check()
    output.append("push eax")

    # calculate args, push args; left-to-right
    args = list(node.find_child("Arguments").children)
    num_args = len(args)
    for arg in args:
        output.extend(gen_expr(arg))
        output.append("push eax")

    # TODO:
    # Get the label corresponding to the method, using the SIT.
    offset = info.get_method_offset(node)
    output.append("mov eax, [esp + %i] ; addr of receiver" % (num_args*4))
    output.append("mov eax, [eax] ; SIT")
    output.append("mov eax, [eax + %i] ; addr of method" % (offset))

    output.append("call eax")
    
    # pop obj addr and args
    output.append("add esp %i" % 4+(num_args*4))

    return output

# Return addr of field access
def gen_field_access(info, node):
    output = ["; gen_field_access"]

    obj_output = gen_expr(info, node.find_child("FieldReceiver"))
    output.extend(obj_output)
    
    util.null_check()

    offset = info.get_field_offset(node)
    output.append("add eax, %i" % (4 + offset))

    return output

# Return addr of array access.
def gen_array_access(info, node):
    output = []
    
    # Get the address of the item we want, dereference into eax.
    output.extend(gen_array_access_addr(info, node))
    output.append('mov eax, [eax]')

    return output

def gen_creation_expr(info, node):
    output = ["; gen_creation_expr"]

    output.append("mov eax, %i" % info.get_size())    
    output.append("push ebx")
    output.append("call __malloc")
    output.append("pop ebx")
    output.append("mov [eax], SIT~%s" % info.class_obj.name)
    output.append("mov [eax+4], SBM~%s" % info.class_obj.name)
    output.append("mov [eax+8], 0")
    output.append("push eax ; this pointer")

    # calculate args, push args; left-to-right
    args = list(node.find_child("Arguments").children)
    num_args = len(args)
    for arg in args:
        output.extend(gen_expr(arg))
        output.append("push eax")

    output.append("call %s" % node.label)

    # pop args
    output.append("add esp %i" % (num_args*4))

    # put "this" on eax
    output.append("pop eax")

    return output

def gen_cast_expr(info, node):
    assert node.name == 'CastExpression'
    output = []

    output.extend(gen_expr(info, node[1]))

    # If these are numeric types, eax already has result, so we are done. So
    # we only need to generate code for typechecking assignability for
    # reference types.
    if primitives.is_numeric(node[1].typ) == False:
        # TODO: Check SBM
        pass

    return output


def gen_add_expr(info, node):
    output = gen_binary_expr_common(info, node)

    # Numbers, just add.
    if primitives.is_numeric(node[0].typ):
        output.append('add eax, ebx')
    
    # If they are objects, have to use String.valueOf().
    else:
        # TODO
        pass

    return output

def gen_subtract_expr(info, node):
    output = gen_binary_expr_common(info, node)

    # Subtract.
    output.append('sub ebx, eax')
    output.append('mov eax, ebx')

    return output

def gen_multiply_expr(info, node):
    output = gen_binary_expr_common(info, node)

    # Multiply.
    output.append('imul eax, ebx')

    return output

def gen_divide_expr(info, node):
    output = gen_binary_expr_common(info, node)

    # We want eax = ebx / eax = expr1 / expr2
    # Sign extend eax into edx:eax.
    output.append('cdq') 

    return output 

def gen_modulo_expr(info, node):
    output = gen_binary_expr_common(info, node)

    # We want eax = ebx % eax = expr1 % expr2
    output.append('cdq')

    return output

def gen_greater_than_expr(info, node):
    pass

# Short circuits on E1, don't use gen_binary_expr_common().
def gen_and_expr(info, node):
    output = []
    label = info.get_jump_label()
    
    return output

# Given an ambiguous name node, generate the code for it.
def gen_ambiguous_name(info, node):
    output = []

    first_significant_identifer = -1
    first_significant_node = None
    for i, identifier_node in enumerate(node.children):
        if identifier_node.decl != None:
            first_significant_identifer = i
            first_significant_node = identifier_node
            break

    assert first_significant_identifer != -1

    # TODO:
    # Depending on the type, follow the correct chain and generate code.
    if first_significant_node.decl.name == 'TypeDeclaration':
        pass

    return output

def gen_this(info, node):
    output = []
    # TODO
    return output

#
# Code generation helpers.
#

# Preamble for method call.
def gen_method_call(info, node):
    output = []
    # TODO
    return output

# Helper for generating code common for all binary expressions.
# After calling this function, LHS is in ebx, RHS is in eax.
def gen_binary_expr_common(info, node):
    output = []

    # Code for left node.
    output.extend(gen_expr(node[0]))

    # Push onto stack.
    output.append('push eax')

    # Code for right node.
    output.extend(gen_expr(node[1]))

    # LHS is in ebx.
    output.append('pop ebx')

    return output

# Helper for getting the address of array elements.
def gen_array_access_lvalue(info, node):
    assert node.name == 'ArrayAccess'
    output = []
    
    # Generate receiver code.
    output.extend(gen_expr(node[0]))

    # Make sure the array we're indexing into is not null.
    output.extend(util.gen_null_check())

    output.append('push eax')

    # Generate index code.
    output.extend(gen_expr(node[1]))

    output.append('pop ebx')

    output.extend(util.gen_array_bounds_check())

    # Skip SIT pointer and length field.
    # Note: java.lang.Object has no fields.
    outout.append('add eax, 2')
    output.append('shl eax, 2') # Multiply index by 4.

    output.append('add eax, ebx') # Address is at array addr + offset.
 
    return output
