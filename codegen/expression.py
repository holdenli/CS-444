import sys

from utils import logging
from utils import primitives

from codegen import util

# Code generation for expressions.

def gen_expr(info, node, method_obj):
    logging.warning("gen_expr: %s" % node)
    
    if node.name == 'Assignment':
        return gen_assignment(info, node, method_obj)
    elif node.name == 'PostfixExpression':
        return gen_expr(info, node[0], method_obj) # Always one expression as child.
    elif node.name == 'Literal':
        return gen_literal_expr(info, node, method_obj)
    elif node.name == 'This':
        return gen_this(info, node, method_obj)
    elif node.name == 'MethodInvocation':
        return gen_method_invocation(info, node, method_obj)
    elif node.name == 'FieldAccess':
        return gen_field_access(info, node, method_obj)
    elif node.name == 'ArrayAccess':
        return gen_array_access(info, node, method_obj)
    elif node.name == 'CreationExpression':
        return gen_creation_expr(info, node, method_obj)
    elif node.name == 'CastExpression':
        return gen_cast_expr(info, node, method_obj)
    elif node.name == 'InstanceofExpression':
        return gen_instanceof_expr(info, node, method_obj)
    
    # Binary expressions.
    elif node.name == 'EqualExpression':
        return gen_equal_expr(info, node, method_obj)
    elif node.name == 'NotEqualExpression':
        return gen_not_equal_expr(info, node, method_obj)
    elif node.name == 'AndExpression':
        return gen_and_expr(info, node, method_obj)
    elif node.name == 'OrExpression':
        return gen_or_expr(info, node, method_obj)
    elif node.name == 'LessThanExpression':
        return gen_less_than_expr(info, node, method_obj)
    elif node.name == 'LessThanEqualExpression':
        return gen_less_than_equal_expr(info, node, method_obj)
    elif node.name == 'GreaterThanExpression':
        return gen_greater_than_expr(info, node, method_obj)
    elif node.name == 'GreaterThanEqualExpression':
        return gen_greater_than_equal_expr(info, node, method_obj)
    elif node.name == 'BinaryAndExpression':
        return gen_binary_and_expr(info, node, method_obj)
    elif node.name == 'BinaryOrExpression':
        return gen_binary_or_expr(info, node, method_obj)
    elif node.name == 'AddExpression':
        return gen_add_expr(info, node, method_obj)
    elif node.name == 'SubtractExpression':
        return gen_subtract_expr(info, node, method_obj)
    elif node.name == 'MultiplyExpression':
        return gen_multiply_expr(info, node, method_obj)
    elif node.name == 'DivideExpression':
        return gen_divide_expr(info, node, method_obj)
    elif node.name == 'ModuloExpression':
        return gen_modulo_expr(info, node, method_obj)
    
    # Unary expressions.
    elif node.name == 'NotExpression':
        return gen_not_expr(info, node, method_obj)
    elif node.name == 'NegateExpression':
        return gen_negate_expr(info, node, method_obj)

    elif node.name == 'Name':
        return gen_ambiguous_name(info, node, method_obj)

    # Bad.
    else:
        logging.error('FATAL ERROR: Invalid node %s for gen_expr()' %
            node.name)
        sys.exit(1)

def gen_assignment(info, node, method_obj):
    output = []

    # Get the *address* of the L-value. This means we call the _addr version
    # of the method.
    if node[0].name == 'FieldAccess':
        output.extend(gen_field_access_addr(info, node[0], method_obj))
    elif node[0].name == 'ArrayAccess':
        output.extend(gen_array_access_addr(info, node[0], method_obj))
    else:
        output.extend(gen_ambiguous_name_addr(info, node[0], method_obj))

    output.append('push eax')

    output.extend(gen_expr(info, node[1], method_obj))

    output.append('pop ebx')

    # TODO: Type check if ebx (L-value) is array element.
    if node[0].name == 'ArrayAccess':
        # output.extend(typecheck_array_assign)
        pass

    output.append('mov [ebx], eax')

    # eax contains the RHS, so we're done.

    return output

def gen_literal_expr(info, node):
    output = []
    if node[0].name == 'DecimalIntegerLiteral':
        output.append("mov eax, %s" % node[0].value.value)

    elif node[0].name == 'BooleanLiteral':
        output.append("mov eax, %s" % int(node[0].value.value == 'true'))

    elif node[0].name == 'CharacterLiteral':
        # TODO: make sure characters are expanded
        output.append("mov eax, %s" % node[0].value.value) # .value = "'c'"

    elif node[0].name == 'StringLiteral':
        # TODO: Create new string.
        pass
    
    elif node[0].name == 'NullLiteral':
        output.append('mov eax, 0')

    return output

# call method
def gen_method_invocation(info, node):
    receiver = node.find_child("MethodReceiver")
    if len(receiver.children) != 0 and receiver[0].typ == None:
        return gen_static_method_invocation(info, node, method_obj)

    output = ["; gen_method_invocation for %s" % node.decl.label]

    # get addr of method receiver
    obj_output = None
    if len(receiver.children) != 0:
        obj_output = gen_expr(info, receiver[0], method_obj)
    else:
        obj_output = gen_this(info, None) 
    output.extend(obj_output)
    output.extend(util.gen_null_check())
    output.append("push eax")

    # calculate args, push args; left-to-right
    args = list(node.find_child("Arguments").children)
    num_args = len(args)
    for arg in args:
        output.extend(gen_expr(info, arg, method_obj))
        output.append("push eax")

    # Get the label corresponding to the method, using the SIT.
    offset = info.get_method_offset(node)
    output.append("mov eax, [esp + %i] ; addr of receiver" % (num_args*4))
    output.append("mov eax, [eax] ; SIT")
    output.append("mov eax, [eax + %i] ; addr of method" % (offset))

    output.append("call eax")
    
    # pop obj addr and args
    output.append("add esp %i" % (4 + num_args*4))

    return output

def gen_static_method_invocation(info, node):
    receiver = node.find_child("MethodReceiver")[0]
    assert receiver.canon != None

    output = ["; gen_static_method_invocation for %s" % node.decl.label]

    # calculate args, push args; left-to-right
    args = list(node.find_child("Arguments").children)
    num_args = len(args)
    for arg in args:
        output.extend(gen_expr(info, arg, method_obj))
        output.append("push eax")

    output.append("call %s" % node.decl.label)

    output.append("add esp %i" % (num_args*4))

    return output

# Return addr of field access
def gen_field_access(info, node):
    output = ["; gen_field_access"]

    obj_output = gen_expr(info, node.find_child("FieldReceiver"))
    output.extend(obj_output)
    
    output.extend(util.gen_null_check())

    offset = info.get_field_offset(node)
    output.append("add eax, %i" % (4 + offset))

    return output

# Return addr of array access.
def gen_array_access(info, node):
    output = []
    
    # Get the address of the item we want, dereference into eax.
    output.extend(gen_array_access_addr(info, node, method_obj))
    output.append('mov eax, [eax]')

    return output

def gen_creation_expr(info, node):
    canon = node.find_child("Type").canon
    if canon.endswith('[]'):
        return gen_creation_expr_array(info, node, method_obj)
    
    output = ["; gen_creation_expr"]

    num_bytes = info.get_size(canon)

    output.append("mov eax, %i" % num_bytes)
    output.append("push ebx") # Safety
    output.append("call __malloc")
    output.append("pop ebx") # Safety

    # Zero out fields.
    output.append('mov eax, %d' % (num_bytes / 4))
    output.extend(util.gen_zero_out(info))

    output.append("mov [eax], SIT~%s" % canon)
    output.append("mov [eax+4], SBM~%s" % canon)
    output.append("mov [eax+8], 0")
    output.append("push eax ; this pointer")

    # calculate args, push args; left-to-right
    args = list(node.find_child("Arguments").children)
    num_args = len(args)
    arg_types = []
    for arg in args:
        output.extend(gen_expr(arg, method_obj))
        output.append("push eax")

        if typecheck.is_array_type(arg[0].canon) == True:
            # '[]'s replaced with '@', so that it can be accepted.
            arg_types.append(arg[0].canon[:-2] + '@')
        else:
            arg_types.append(arg[0].canon)

    label = 'CONSTRUCTOR~%s.%s~%s' % (canon, canon, '~'.join(arg_types))
    output.append("call %s" % label)

    # pop args
    output.append("add esp %i" % (num_args*4))

    # put "this" on eax
    output.append("pop eax")

    return output

def gen_creation_expr_array(info, node, method_obj):
    canon = node.find_child("Type").canon
    assert not canon.endswith('[]')
    canon = canon[:-2]
    if canon in primitives.primitive_types:
        canon = "@" + canon # add @ infront of primitives for SBM

    output = ["; gen_creation_expr_array"]

    # put length of array in eax
    args = node.find_child("Arguments").children
    num_args = len(args)
    if num_args == 1:
        output.extend(gen_expr(info, args[0], method_obj)) # Array length in eax.
    else:
        assert num_args == 0
        output.append("mov eax 0")

    # Calculate number of bytes we need for the array.
    output.append('push eax') # Save array length.
    outout.append('add eax, 4')
    output.append('push eax') # Save num words.
    output.append('shl eax, 2') # Multiply index (offset) by 4.

    # Allocate. eax has addr. 
    output.append('call __malloc')

    # Zero out array.
    output.append('pop ebx') # Num words.
    output.extend(util.gen_zero_out(info)) # eax = ptr, ebx = num words

    output.append('pop ebx') # Restore array length.

    # Object metadata.
    output.append("mov [eax], SIT~%s" % util.object_class_name) # java.lang.object
    output.append("mov [eax+4], SBM~%s" % canon)
    output.append("mov [eax+8], 1")
    output.append("mov [eax+12], ebx") # Length

    return output

def gen_cast_expr(info, node, method_obj):
    assert node.name == 'CastExpression'
    output = []

    output.extend(gen_expr(info, node[1], method_obj))

    # If these are numeric types, eax already has result, so we are done. So
    # we only need to generate code for typechecking assignability for
    # reference types.
    if primitives.is_numeric(node[1].typ) == False:
        # TODO: Check SBM
        pass

    return output

def gen_add_expr(info, node, method_obj):
    output = []

    # Numbers, just add.
    if primitives.is_numeric(node[0].typ) and primitives.is_numeric(node[1].typ):
        output.extend(gen_binary_expr_common(info, node, method_obj))
        output.append('add eax, ebx')
    
    # If they are objects, we do the following:
    # 1. Use String.valueOf() on each operand.
    # 2. Create a new empty string.
    # 3. concat both strings into the new string, using 
    else:

        # Convert LHS to a string.
        output.extend(gen_string_valueof(info, node[0], method_obj))
        output.append('push eax')

        # Convert RHS to a string.
        output.extend(gen_string_valueof(info, node[1], method_obj))
        output.append('push eax')

        # LHS is at esp+8, RHS is at esp+4. We need to make a new empty string
        # to concat both onto.

# Evaluates the node, then calls the correct java.lang.String.valueOf function
# based on the type of the node (assumed to be in eax).
def gen_string_valueof(info, node):
    output = []

    # Evaluate node. Result is in eax.
    output.extend(gen_expr(info, node, method_obj))
    
    # Based on the type, call the correct method. Primitives have their own
    # version, objects all use the java.lang.Object version.
    valueof_method_lbl = ''
    if primitives.is_numeric(node.typ) or node.typ == 'Boolean':
        valueof_method_lbl = 'STATICMETHOD~java.lang.String.valueOf~%s' % node[0].typ
    else:
        valueof_method_lbl = 'STATICMETHOD~java.lang.String.valueOf~java.lang.Object'
    output.append('push eax')
    output.append('call %s' % valueof_method_lbl)

    return output # result is in eax


def gen_subtract_expr(info, node):
    output = gen_binary_expr_common(info, node, method_obj)

    # Subtract.
    output.append('sub ebx, eax')
    output.append('mov eax, ebx')

    return output

def gen_multiply_expr(info, node):
    output = gen_binary_expr_common(info, node, method_obj)

    # Multiply.
    output.append('imul eax, ebx')

    return output

def gen_divide_expr(info, node):
    output = gen_binary_expr_common(info, node, method_obj)

    # E1 is in ebx, E2 is in eax
    # We want eax = E1 / E2
    output.append('mov ecx, eax') # ecx = E2
    output.append('mov eax, ebx') # eax = E1
    output.append('mov ebx, ecx') # ebx = E2

    # Sign extend eax into edx:eax, then divide.
    output.append('cdq')
    output.append('idiv ebx') # result in eax

    return output 

def gen_modulo_expr(info, node):
    output = gen_binary_expr_common(info, node)

    # E1 is in ebx, E2 is in eax
    # We want eax = E1 % E2
    output.append('mov ecx, eax') # ecx = E2
    output.append('mov eax, ebx') # eax = E1
    output.append('mov ebx, ecx') # ebx = E2

    # Sign extend eax into edx:eax, then divide.
    output.append('cdq')
    output.append('idiv ebx')
    output.append('mov eax, edx')

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
    output.extend(gen_expr(info, node[0], method_obj))

    # Push onto stack.
    output.append('push eax')

    # Code for right node.
    output.extend(gen_expr(info, node[1, method_obj]))

    # LHS is in ebx.
    output.append('pop ebx')

    return output

# Helper for getting the address of array elements.
def gen_array_access_addr(info, node, method_obj):
    assert node.name == 'ArrayAccess'
    output = []
    
    # Generate receiver code.
    output.extend(gen_expr(info, node[0][0], method_obj))

    # Make sure the array we're indexing into is not null.
    output.extend(util.gen_null_check())

    output.append('push eax')

    # Generate index code.
    output.extend(gen_expr(info, node[1], method_obj))

    output.append('pop ebx')

    output.extend(util.gen_array_bounds_check())

    # Skip SIT pointer and length field.
    # Note: java.lang.Object has no fields.
    output.append('add eax, 4')
    output.append('shl eax, 2') # Multiply index (offset) by 4.

    output.append('add eax, ebx') # Address is at array addr + offset.
 
    return output

# Creates a new string from the input (or empty string) and puts the reference
# in eax.
def gen_new_string(info, node, init_str):
    output = []    

    # First we make a char array with length equal to size of init_str
    num_chars = len(init_str)
    #output.append('mov eax
    output.extend()

    return output

