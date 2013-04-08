import sys

import typecheck

from utils import logging
from utils import primitives
from utils import class_hierarchy

from codegen import util

# Code generation for expressions.

def gen_expr(info, node, method_obj):
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

    """
    # TODO: Type check if ebx (L-value) is array element.
    if node[0].name == 'ArrayAccess':
        end_lbl = info.get_jump_label()

        canon = node[0][0][0].typ

        if primitives.is_primitive(canon):
            canon = "@" + canon

        # check null
        output.append("cmp eax, 0")
        output.append("je %s" % end_lbl)

        output.append('push eax')

        util.gen_assignability_check(info, canon)

        output.append("cmp eax, 0")
        output.append("je __exception")

        output.append('pop eax')

        output.append(end_lbl + ":")
    """

    output.append('mov dword [ebx], eax')

    # eax contains the RHS, so we're done.

    return output

def gen_literal_expr(info, node, method_obj):
    output = []
    if node[0].name == 'DecimalIntegerLiteral':
        output.append("mov eax, %s" % node[0].value.value)

    elif node[0].name == 'BooleanLiteral':
        output.append("mov eax, %d" % int(node[0].value.value == 'true'))

    elif node[0].name == 'CharacterLiteral':
        output.append("mov eax, %d" % ord(node[0].value.value[0])) # .value = "'c'"

    elif node[0].name == 'StringLiteral':
        output.extend(gen_new_string(info, node[0].value.value))
    
    elif node[0].name == 'NullLiteral':
        output.append('mov eax, 0')

    return output

# call method
def gen_method_invocation(info, node, method_obj):
    receiver = node.find_child("MethodReceiver")
    if len(receiver.children) != 0 and receiver[0].typ == None:
        return gen_static_method_invocation(info, node, method_obj)

    output = ["; START gen_method_invocation for %s" % node.decl.label]

    # get addr of method receiver
    output.append("; Eval receiver")
    obj_output = None
    if len(receiver.children) != 0:
        obj_output = gen_expr(info, receiver[0], method_obj)
    else:
        obj_output = gen_this(info, None, method_obj) 
    output.extend(obj_output)
    output.extend(util.gen_null_check())
    output.append("push eax")

    # calculate args, push args; left-to-right
    args = list(node.find_child("Arguments").children)
    num_args = len(args)
    output.append("; Eval %i args" % num_args)
    for arg in args:
        output.extend(gen_expr(info, arg, method_obj))
        output.append("push eax")

    # Get the label corresponding to the method, using the SIT.
    output.append("; Get method impl")
    offset = info.get_method_offset(node)
    output.append("mov eax, [esp + %i] ; addr of receiver" % (num_args*4))
    output.append("mov eax, [eax] ; SIT")
    output.append("mov eax, [eax + %i] ; addr of method" % (offset))

    output.append("call eax")
    
    # pop obj addr and args
    output.append("add esp, %i ; pop this and args" % (4 + num_args*4))

    output.append("; END gen_method_invocation")

    return output

def gen_static_method_invocation(info, node, method_obj):
    receiver = node.find_child("MethodReceiver")[0]
    assert receiver.canon != None

    output = ["; START gen_static_method_invocation for %s" % node.decl.label]

    # calculate args, push args; left-to-right
    args = list(node.find_child("Arguments").children)
    num_args = len(args)
    output.append("; Eval %i args" % num_args)
    for arg in args:
        output.extend(gen_expr(info, arg, method_obj))
        output.append("push eax")

    output.append("call %s" % node.decl.label)

    output.append("add esp, %i ; pop args" % (num_args*4))

    output.append("; END gen_static_method_invocation")

    return output

# Return addr of field access
def gen_field_access(info, node, method_obj):
    output = ["; gen_field_access"]

    # Gets the field receiver.
    output.extend(gen_field_access_addr(info, node, method_obj))
    output.append('mov eax, [eax]')

    return output

# Return addr of array access.
def gen_array_access(info, node, method_obj):
    output = []
    
    # Get the address of the item we want, dereference into eax.
    output.extend(gen_array_access_addr(info, node, method_obj))
    output.append('mov eax, [eax]')

    return output

def gen_creation_expr(info, node, method_obj):
    canon = node.find_child("Type").canon
    if canon.endswith('[]'):
        return gen_creation_expr_array(info, node, method_obj)
    
    output = ["; START gen_creation_expr"]

    # Number of bytes we will malloc (including metadata).
    num_bytes = info.get_size(canon)

    output.append("mov eax, %i" % num_bytes)
    output.append("push ebx") # Safety
    output.append("call __malloc")
    output.append("pop ebx") # Safety

    # Zero out fields.
    output.append('mov ebx, %d' % (num_bytes / 4))
    output.extend(util.gen_zero_out(info))

    output.append("mov dword [eax], SIT~%s" % canon)
    output.append("mov dword [eax+4], SBM~%s" % canon)
    output.append("mov dword [eax+8], 0") # Not an array, so 0.
    output.append("push eax ; this pointer")

    # calculate args, push args; left-to-right
    args = list(node.find_child("Arguments").children)
    num_args = len(args)
    arg_types = []
    for arg in args:
        output.extend(gen_expr(info, arg, method_obj))
        output.append("push eax")

        if typecheck.is_array_type(arg.typ) == True:
            # '[]'s replaced with '@', so that it can be accepted.
            arg_types.append(arg.typ[:-2] + '@')
        else:
            arg_types.append(arg.typ)

    constructor_name = canon.split(".")[-1]
    label = 'CONSTRUCTOR~%s.%s~%s' % (canon, constructor_name, '~'.join(arg_types))
    output.append("call %s" % label)

    # pop args
    output.append("add esp, %i" % (num_args*4))

    # put "this" on eax
    output.append("pop eax")

    output.append("; END gen_creation_expr")

    return output

def gen_creation_expr_array(info, node, method_obj):
    canon = node.find_child("Type").canon
    assert canon.endswith('[]')
    canon = canon[:-2]
    if canon in primitives.primitive_types:
        canon = "@" + canon # add @ infront of primitives for SBM

    output = ["; START gen_creation_expr_array"]

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
    output.append('add eax, 4')
    output.append('push eax') # Save num words.
    output.append('shl eax, 2') # Multiply index (offset) by 4.

    # Allocate. eax has addr. 
    output.append('call __malloc')

    # Zero out array.
    output.append('pop ebx') # Num words.
    output.extend(util.gen_zero_out(info)) # eax = ptr, ebx = num words

    output.append('pop ebx') # Restore array length.

    # Object metadata.
    output.append("mov dword [eax], SIT~java.lang.Object")
    output.append("mov dword [eax+4], SBM~%s" % canon)
    output.append("mov dword [eax+8], 1")
    output.append("mov dword [eax+12], ebx") # Length

    output.append("; END gen_creation_expr_array")

    return output

def gen_cast_expr(info, node, method_obj):
    end_lbl = info.get_jump_label()

    output = ["; gen_cast_expr"]

    output.extend(gen_expr(info, node[1], method_obj))

    if primitives.is_primitive(node[1].typ):
        return output

    # check null
    output.append("cmp eax, 0")
    output.append("je %s" % end_lbl)

    output.append("push eax")

    canon = node[0].canon
    util.gen_assignability_check(info, canon)

    output.append("cmp eax, 0")
    output.append("je __exception")

    output.append("pop eax")

    output.append(end_lbl + ":")

    return output

def gen_binary_and_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

    label = info.get_jump_label()
    output.append("and eax, ebx")

    return output

def gen_binary_or_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

    label = info.get_jump_label()
    output.append("or eax, ebx")

    return output

def gen_add_expr(info, node, method_obj):
    output = []

    # Numbers, just add.
    if primitives.is_numeric(node[0].typ) and primitives.is_numeric(node[1].typ):
        output.extend(gen_binary_expr_common(info, node, method_obj))
        output.append('add eax, ebx')
    
    # If they are objects, we do the following:
    # 1. Use String.valueOf() on each operand.
    # 2. Do a LHS.concat(RHS), which returns a new string.
    else:

        # Convert LHS to a string.
        output.extend(gen_string_valueof(info, node[0], method_obj))
        output.append('push eax')

        # Convert RHS to a string.
        output.extend(gen_string_valueof(info, node[1], method_obj))
        output.append('push eax')

        # Receiver is LHS, Argument is RHS (already done!), just need to call
        # the correct method.
        output.append('call METHOD~java.lang.String.concat~java.lang.String')

        # Jump back.
        output.append('add esp, 8')

    return output

# Evaluates the node, then calls the correct java.lang.String.valueOf function
# based on the type of the node (assumed to be in eax).
def gen_string_valueof(info, node, method_obj):
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

def gen_subtract_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

    # Subtract.
    output.append('sub ebx, eax')
    output.append('mov eax, ebx')

    return output

def gen_multiply_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

    # Multiply.
    output.append('imul eax, ebx')

    return output

def gen_divide_expr(info, node, method_obj):
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

def gen_modulo_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

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

def gen_equal_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

    label = info.get_jump_label()

    # Test that ebx == eax (E1 >= E2)
    output.append('mov ecx, 0x1')
    output.append('cmp ebx, eax')
    output.append('je %s' % label)
    output.append('mov ecx, 0')
    output.append(label + ':')
    output.append('mov eax, ecx')

    return output

def gen_not_equal_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

    label = info.get_jump_label()

    # Test that ebx != eax (E1 >= E2)
    output.append('mov ecx, 0x1')
    output.append('cmp ebx, eax')
    output.append('jne %s' % label)
    output.append('mov ecx, 0')
    output.append(label + ':')
    output.append('mov eax, ecx')

    return output

def gen_greater_than_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

    label = info.get_jump_label()

    # Test that ebx < eax (E1 < E2)
    output.append('mov ecx, 0x1')
    output.append('cmp ebx, eax')
    output.append('jg %s' % label)
    output.append('mov ecx, 0')
    output.append(label + ':')
    output.append('mov eax, ecx')

    return output

def gen_greater_than_equal_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

    label = info.get_jump_label()

    # Test that ebx >= eax (E1 >= E2)
    output.append('mov ecx, 0x1')
    output.append('cmp ebx, eax')
    output.append('jge %s' % label)
    output.append('mov ecx, 0')
    output.append(label + ':')
    output.append('mov eax, ecx')

    return output

def gen_less_than_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

    label = info.get_jump_label()

    # Test that ebx < eax (E1 < E2)
    output.append('mov ecx, 0x1')
    output.append('cmp ebx, eax')
    output.append('jl %s' % label)
    output.append('mov ecx, 0')
    output.append(label + ':')
    output.append('mov eax, ecx')

    return output

def gen_less_than_equal_expr(info, node, method_obj):
    output = gen_binary_expr_common(info, node, method_obj)

    label = info.get_jump_label()

    # Test that ebx <= eax (E1 <= E2)
    output.append('mov ecx, 0x1')
    output.append('cmp ebx, eax')
    output.append('jle %s' % label)
    output.append('mov ecx, 0')
    output.append(label + ':')
    output.append('mov eax, ecx')

    return output

# Short circuits on E1, don't use gen_binary_expr_common().
def gen_and_expr(info, node, method_obj):
    output = []
    label = info.get_jump_label()

    output.extend(gen_expr(info, node[0], method_obj))
    output.append('mov ecx, 0') # result is false by default
    output.append('cmp eax, 0') # now we test..
    output.append('je %s' % label) # if false, we end up at the BOTTOM

    # the result was true! now try the second expr:
    output.extend(gen_expr(info, node[1], method_obj))
    output.append('mov ecx, 0')
    output.append('cmp eax, 0') # we test again..
    output.append('je %s' % label) # if false, we end up at the BOTTOM
    output.append('mov ecx, 1')

    output.append('%s:' % label) # BOTTOM!
    output.append('mov eax, ecx')

    return output

# Short circuits on E1, don't use gen_binary_expr_common().
def gen_or_expr(info, node, method_obj):
    output = []
    label = info.get_jump_label()

    output.extend(gen_expr(info, node[0], method_obj))
    output.append('mov ecx, 1') # result is true by default
    output.append('cmp eax, 0') # now we test..
    output.append('jne %s' % label) # if NOT false (true), we end up at the BOTTOM

    # try again with the right operand..
    output.extend(gen_expr(info, node[1], method_obj))
    output.append('mov ecx, 1') # result is true by default
    output.append('cmp eax, 0') # now we test..
    output.append('jne %s' % label) # jump to the bottom if true
    output.append('mov eax, 0')

    output.append('%s:' % label) # BOTTOM
    output.append('mov eax, ecx');

    return output

# Given an ambiguous name node, generate the code for it.
def gen_ambiguous_name(info, node, method_obj):
    output = ["; START gen_ambiguous_name"]

    output.extend(gen_ambiguous_name_addr(info, node, method_obj))
    output.extend(util.gen_null_check())
    output.append('mov eax, [eax]')

    output.append('; END gen_ambiguous_name')

    return output

# Note: node is unused and can be junk.
def gen_this(info, node, method_obj):
    output = []

    # 'this' is found before (i.e., below) all params.
    offset = len(method_obj.params) * 4
    output.append('mov eax, [ebp+%d]' % (offset + 8))

    return output

def gen_instanceof_expr(info, node, method_obj):
    end_lbl = info.get_jump_label()

    output = ["; gen_instanceof_expr"]

    output.extend(gen_expr(info, node[0], method_obj))

    # check null
    output.append("cmp eax, 0")
    output.append("je %s" % end_lbl)

    canon = node[1].canon

    util.gen_assignability_check(info, canon)

    output.append(end_lbl + ":")

    return output

def gen_not_expr(info, node, method_obj):
    output = []
    output.extend(gen_expr(info, node[0], method_obj))

    label = info.get_jump_label()

    output.append('mov ebx, 0') # test if exp == 0
    output.append('cmp eax, ebx')
    output.append('mov eax, 1') # set result to 1
    output.append('je %s' % label) # if exp == 0, keep it 1
    output.append('mov eax, 0')
    output.append(label + ':')

    return output

def gen_negate_expr(info, node, method_obj):
    output = []
    output.extend(gen_expr(info, node[0], method_obj))

    output.append('mov ebx, eax') # ebx = E1
    output.append('mov eax, 0') # eax = 0
    output.append('sub eax, ebx') # eax = 0 - E1

    return output

#
# Code generation helpers.
#

# Helper for generating code common for all binary expressions.
# After calling this function, LHS is in ebx, RHS is in eax.
def gen_binary_expr_common(info, node, method_obj):
    output = []

    # Code for left node.
    output.extend(gen_expr(info, node[0], method_obj))

    # Push onto stack.
    output.append('push eax')

    # Code for right node.
    output.extend(gen_expr(info, node[1], method_obj))

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

    # Generate index code into ebx.
    output.extend(gen_expr(info, node[1], method_obj))
    output.append('mov ebx, eax')

    # eax has array.
    output.append('pop eax')

    # Check that index is within array bounds.
    output.extend(util.gen_array_bounds_check())

    # Skip SIT pointer and length field.
    # Note: java.lang.Object has no fields.
    output.append('add eax, 4')
    output.append('shl eax, 2') # Multiply index (offset) by 4.

    output.append('add eax, ebx') # Address is at array addr + offset.
 
    return output

def gen_field_access_addr(info, node, method_obj):
    output = []

    # Gets the field receiver.
    obj_output = gen_expr(info, node.find_child("FieldReceiver")[0], method_obj)
    output.extend(obj_output)
    
    output.extend(util.gen_null_check())

    if typecheck.is_array_type(node[1][0].typ) == True: # Array
        output.append('add eax, %d' % 12)

    else: # Object.
        offset = info.get_field_offset(node)
        output.append("add eax, %i" % (12 + offset))

    return output

def gen_ambiguous_name_addr(info, node, method_obj):
    assert node.name == 'Name'

    output = ['; gen_ambiguous_name_addr']

    # Loop through each identifier node, looking for a significant node.
    significant_node = None
    significant_index = -1
    for i, id_node in enumerate(node.children):
        if hasattr(id_node, 'decl') or hasattr(id_node, 'canon'):
            significant_node = id_node
            significant_index = i
            break

    assert significant_index != -1 # Did not find anything, error.

    # We have Type.something, so there must be a next node.
    # This is a Static field access.
    id_node = significant_node
    i = significant_index
    prev_type = None
    if hasattr(id_node, 'canon') and id_node.canon != None:
        assert (i + 1) < len(node.children)

        # Return address of static field.
        next_node = node[i + 1].decl # decl should be static field ASTNode
        assert next_node.name == 'FieldDeclaration'
        assert 'static' in next_node.modifiers
        output.append('mov eax, %s' % next_node.label)

        i += 2 # Processed 2 nodes.
        prev_type = next_node[1].canon # Get type from Type node

    # We have local_var.something. Move its addr to eax.
    elif id_node.decl.name == 'LocalVariableDeclaration':
        assert i == 0 # Local variable must be first identifier.

        # Get the offset from the frame pointer.
        output.append('mov eax, ebp')
        local_var_offset = id_node.decl.frame_offset * 4
        output.append('add eax, %d' % local_var_offset)

        i += 1
        prev_type = id_node.decl[0].canon # Get type from Type node

    # We have a parameter.something. Move its addr to eax.
    elif id_node.decl.name == 'Parameter':
        assert i == 0 # Parameter must be first identifier.

        # Get the offset from the frame pointer.
        output.append('mov eax, ebp')
        param_offset = (id_node.decl.frame_offset * 4)
        output.append('add eax, %d' % param_offset)

        i += 1
        prev_type = id_node.decl[0].canon # Get type from Type node

    # We have an implicit 'this' on an instance field.
    elif id_node.decl.name == 'FieldDeclaration':
        assert i == 0 # Field declaration must be first identifier.

        # Get this into eax.
        output.extend(gen_this(info, None, method_obj))

        # If the field type is array, we must get the array field.
        offset = 0
        if typecheck.is_array_type(id_node.decl[1].canon):
            offset = 12
        else:
            receiver_type = info.class_obj.name
            field_name = id_node.decl.obj.name
            offset = info.get_field_offset_from_field_name(receiver_type, field_name)
            offset += 12
        prev_type = id_node.decl[1].canon # Generic type.

        # Load the field address offset.
        output.append('add eax, %d' % offset)

        i += 1

    # All the remaining things are instance fields. We have the address in eax
    # already, so we just keep going.
    while i < len(node.children):
        assert i >= 1
        assert prev_type != None
        field_node = node[i]

        assert field_node.decl.name in ['FieldDeclaration',
            'FakeFieldDeclaration']

        # Nullcheck and dereference the previous result into eax.
        output.extend(util.gen_null_check())
        output.append('mov eax, [eax]')

        # Calculate the offset of the field.
        offset = 0

        # Array; length has type Int.
        if typecheck.is_array_type(prev_type):
            assert i == (len(node.children) - 1) # Must be last element.
            offset = 12
            prev_type = 'Int'

        # Object. Must search up the object's type (in prev_type) in the field
        # index and get the offset.
        else:
            prev_type_field_list = info.field_index[prev_type]
            field_name = field_node.decl.obj.name
            temp = class_hierarchy.Temp_Field(field_name)
            offset = (prev_type_field_list.index(temp) * 4) + 12
            # Keep the type.
            prev_type = field_node.decl[1].canon

        output.append('add eax, %d' % offset)

        i += 1   
        
    output.append('; end of gen_ambiguous_name_addr')    

    return output

# Creates a new string from the input (or empty string) and puts the reference
# in eax.
def gen_new_string(info, init_str):
    output = ['; gen_new_string = %s' % init_str]

    # First we make a char array with length equal to size of init_str
    num_chars = len(init_str)

    # Make a new array.
    output = ["; gen_new_string"]

    # Put number of bytes in eax.
    output.append('mov eax, %d' % ((num_chars + 4) * 4))

    # Calculate number of bytes we need for the array.

    # Allocate. eax has addr. 
    output.append('call __malloc')

    # Zero out array.
    output.append('mov ebx, %d' % (num_chars + 4))
    output.extend(util.gen_zero_out(info)) # eax = ptr, ebx = num words

    output.append('pop ebx') # Restore array length.

    # Object metadata.
    output.append("mov dword [eax], SIT~java.lang.Object")
    output.append("mov dword [eax+4], SBM~@Char")
    output.append("mov dword [eax+8], 1")
    output.append("mov dword [eax+12], %d" % num_chars) # Length

    # Fill in elems.
    offset = 0
    for c in init_str:
        output.append('mov dword [eax+%d], %d' % (((offset + 4) * 4), ord(c)))
        offset += 1

    # Back up array.
    output.append('push eax')

    # Call a new string.

    # Number of bytes we will malloc (including metadata).
    num_bytes = info.get_size('java.lang.String')

    output.append("mov eax, %i" % num_bytes)
    output.append("call __malloc")

    # Zero out fields.
    output.append('mov ebx, %d' % (num_bytes / 4))
    output.extend(util.gen_zero_out(info))

    output.append("mov dword [eax], SIT~java.lang.String")
    output.append("mov dword [eax+4], SBM~java.lang.String")
    output.append("mov dword [eax+8], 0") # Not an array, so 0.

    # Get the char array.
    output.append('pop ebx')

    # Push the string addr, and the char array as an argument.
    output.append("push eax ; this pointer")
    output.append('push ebx')

    # Call the constructor.
    constructor_label = 'CONSTRUCTOR~java.lang.String.String~Char@'
    output.append("call %s" % constructor_label)

    # pop args (only 1)
    output.append("add esp, 4")

    # put "this" on eax
    output.append("pop eax")

    output.append("; END gen_new_string")
    return output

