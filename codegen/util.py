from codegen import expression

# check if c is a supertype of the object at eax
def gen_assignability_check(info, c):
    output = ["; assignability check"]

    output.append("push eax")

    output.append("mov eax, [eax + 4] ; SBM")

    offset = 0
    if c == "Boolean":
        offset = len(info.class_list)
    elif c == "Byte":
        offset = len(info.class_list) + 1
    elif c == "Char":
        offset = len(info.class_list) + 2
    elif c == "Int":
        offset = len(info.class_list) + 3
    elif c == "Short":
        offset = len(info.class_list) + 4
    else:
        offset = info.class_list.index(c) * 4
    output.append("mov eax, [eax + %i]" % offset)

    output.append("cmp eax, 0")
    output.append("je __exception")
    output.append("pop eax")

    return output

# Check if eax is null(0)
# If so, throw exception
def gen_null_check():
    output = ["; null check"]

    output.append("cmp eax, 0")
    output.append("je __exception")

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

# Check that the type of eax is assignable to ebx.
# ???
def gen_check_type(info, lhs, rhs):
    output = []
    
    return output
