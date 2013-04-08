# check if c (canon) is a supertype of the object at eax; return true or false on eax
def gen_assignability_check(info, canon):
    is_array = False
    if canon.endswith("[]"):
        canon = canon[:-2]
        is_array = True

    end_lbl = info.get_jump_label()
    normal_lbl = info.get_jump_label()

    output = ["; assignability check"]

    # array check
    # if array then make sure canon is array type or
    # cloneable, serializable, or object
    output.append("mov eax, [eax + 8] ; Array flag")
    if canon in ["java.lang.Object", "java.io.Serializable", "java.lang.Cloneable"]:
        output.append("cmp eax, 1") # Test if runtime type is an array.
        output.append('je %s' % end_lbl) # If it's an array, we're done, since eax has 1.
        output.append('jmp %s' % normal_lbl) # Perform a regular object check.

    # We're comparing against array, so we test array assignability.
    elif is_array:
        output.append("cmp eax, 1")
        output.append("je %s" % normal_lbl)
        # Otherwise, fall through to false.

    else:
        output.append("cmp eax, 0")
        output.append("je %s" % normal_lbl)

    # "false" code
    output.append("mov eax, 0")
    output.append("jmp %s" % end_lbl)

    # normal code: look up SBM
    output.append(normal_lbl + ":")

    output.append("mov eax, [eax + 4] ; SBM")

    offset = 0
    if canon == "Boolean":
        offset = len(info.class_list)
    elif canon == "Byte":
        offset = len(info.class_list) + 1
    elif canon == "Char":
        offset = len(info.class_list) + 2
    elif canon == "Int":
        offset = len(info.class_list) + 3
    elif canon == "Short":
        offset = len(info.class_list) + 4
    else:
        c = info.class_index[canon]
        offset = info.class_list.index(c) * 4
    output.append("mov eax, [eax + %i]" % offset)

    output.append(end_lbl + ":")

    return output

# Check if eax is null(0)
# If so, throw exception
def gen_null_check():
    output = ["; null check"]

    output.append("cmp eax, 0")
    output.append("je __exception")

    return output

# Checks that the index being accessed (in ebx) is within bounds of the array
# (at eax).
def gen_array_bounds_check():
    output = ["; array bounds check"]

    output.append('mov ecx, [eax+12]')
    output.append('cmp ebx, ecx') # if index >= length, error
    output.append('jae __exception') # unsigned comparison

    return output

# Evaluate node, jump to label if it's False
def gen_iffalse(info, node, label):
    output = []
    
    # Evaluate the expression.
    eval_output = expression.gen_expr(node)
    output.extend(eval_output)

    # compare and jump
    output.append("cmp eax, 0")
    output.append("je %s" % label)

    output.append(label)
    return output

def gen_iftrue(info, node, label):
    output = []
    
    # Evaluate the expression.
    eval_output = expression.gen_expr(node)
    output.extend(eval_output)

    # compare and jump
    output.append("cmp eax, 0")
    output.append("jne %s" % label)

    output.append(label)
    return output

# Zeroes out ebx words, starting from ebx.
# Essentially does the the following:
#   eax = address of object
#   ebx = number of words to zero out
#   for (ecx = 0; ecx != ebx; ecx++) {
#       [eax+4*ecx] <- 0
#   }
def gen_zero_out(info):
    loop_lbl = info.get_jump_label()
    end_lbl = info.get_jump_label()

    output = ['; begin gen_zero_out']
    output.append('mov ecx, 0')
    output.append(loop_lbl + ':')
    output.append('cmp ecx, ebx')
    output.append('je %s' % end_lbl) # if ecx == ebx, done
    '''
    output.append('mov edx, ecx')
    output.append('shl edx, 2')
    output.append('add edx, eax')
    output.append('mov [edx], 0') # eax[ecx] = 0
    '''
    output.append('mov dword [eax + 4 * ecx], 0') # eax[ecx] = 0
    output.append('add ecx, 0x1') # ecx++
    output.append('jmp %s' % loop_lbl)
    output.append(end_lbl + ':')
   
    output.append('; end gen_zero_out')

    return output

