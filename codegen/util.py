from codegen import expression

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

