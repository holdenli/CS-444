# Code generation for expressions.

def gen_expr(info, node):
    if node.name == 'Assignment':
        return gen_assignment(info, node)

def gen_assignment(info, node):
    output = []

    # Assignment = [Name, lots of expression choices .. ]
    if node[1].name == 'PostfixExpression':
        output.extend(gen_postfix_expr(info, node[1]))

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

def gen_method_invocation(info, node):
    output = []
    

    # Get the label.
    node.label = get_method_label(node.decl)

    # TODO:
    # Get the label corresponding to the method, using the SIT.

    return output

def gen_field_access(info, node):
    output = []
    return output


def gen_array_access(info, node):
    pass

def gen_creation_expr(info, node):
    pass

def gen_add_expr(info, node):
    output = gen_binary_common(info, node)

    # If they are objects, have to use String.valueOf().
    if primitives.is_numeric(node[0].typ):
        # TODO
        pass
    else:
        # Add.
        output.append('add eax, ebx')

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
    

    output.append()
    return output 

def gen_modulo_expr(info, node):
    output = gen_binary_expr_common(info, node)

    # We want eax = ebx % eax = expr1 % expr2

    output.append()
    return output

def gen_greater_than_expr(info, node):
    pass

# Short circuits on E1, don't use gen_binary_expr_common().
def gen_and_expr(info, node):
    output = []
    label = info.get_jump_label()
    
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

def gen_iffalse(info, node, label):
    output = []
    
    # Evaluate the expression.
    
    
    output.append(label)
    return output

