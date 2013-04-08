import sys

from utils import logging

from codegen import expression

#
# Codegen for statements.
#

def gen_stmt(info, node, method_obj):
    if node.name == 'LocalVariableDeclaration':
        return gen_local_variable_decl(info, node, method_obj)
    elif node.name == 'Block':
        return gen_block(info, node, method_obj)
    elif node.name == 'ExpressionStatement':
        return gen_expr_stmt(info, node, method_obj)
    elif node.name == 'ReturnStatement':
        return gen_return_stmt(info, node, method_obj)
    elif node.name == 'IfStatement':
        return gen_if_stmt(info, node, method_obj)
    elif node.name == 'WhileStatement':
        return gen_while_stmt(info, node, method_obj)
    elif node.name == 'ForStatement':
        return gen_for_stmt(info, node, method_obj)
    elif node.name == 'EmptyStatement':
        return []

    # Bad.
    else:
        logging.error('FATAL ERROR: Invalid node %s for gen_stmt()' %
            node.name)
        sys.exit(1)

def gen_local_variable_decl(info, node, method_obj):
    output = ["; gen_local_variable_decl on %s" % node]

    # Generate the initialization code.
    output.extend(expression.gen_expr(info, node[2][0], method_obj))

    # Get the offset.
    offset = node.frame_offset * 4
    output.append('mov ebx, %d' % offset)

    # Calculate address and assign.
    output.append('mov [ebp+ebx], eax')

    return output

def gen_block(info, node, method_obj):
    output = []

    # generate local variables for this block
    '''
    for i, (var_name, var_decl) in enumerate(node.env.names.items()):
        info.local_vars[var_name] = (i, var_decl)
    '''

    for stmt in node.children:
        output.extend(gen_stmt(info, stmt, method_obj))

    return output

def gen_expr_stmt(info, node, method_obj):
    output = []
    output.extend(expression.gen_expr(info, node[0], method_obj))
    return output

def gen_if_stmt(info, node, method_obj):
    output = []

    else_label = info.get_jump_label()
    end_label = info.get_jump_label()

    # Check condition.
    output.extend(expression.gen_expr(info, node[0], method_obj))
    output.append('mov ebx, 0')
    output.append('cmp eax, ebx')
    output.append('je %s' % else_label) # statement is false, jump to else

    # True path.
    output.extend(gen_stmt(info, node[1], method_obj))
    output.append('jmp %s' % end_label)

    # False path.
    output.append(else_label + ':')
    if len(node.children) == 3: # If there's an else condition, gen some code
        output.extend(gen_stmt(info, node[2], method_obj))

    output.append(end_label + ':')

    return output

def gen_for_stmt(info, node, method_obj):
    output = []

    # Initialize, if any.
    if len(node[0].children) == 1:
        if node[0][0].name == 'LocalVariableDeclaration':
            output.extend(gen_local_variable_decl(info, node[0][0], method_obj))
        else: # expression
            output.extend(expression.gen_expr(info, node[0][0], method_obj))

    loop_lbl = info.get_jump_label()
    end_lbl = info.get_jump_label()

    output.append(loop_lbl + ':')

    # Generate cond, if any.
    if len(node[1].children) == 1:
        output.extend(expression.gen_expr(info, node[1][0], method_obj))
        output.append('mov ebx, 0')
        output.append('cmp eax, ebx')
        output.append('je %s' % end_lbl) # If false, go to end.

    # Generate body, if any.
    if len(node[3].children) == 1:
        output.extend(gen_stmt(info, node[3][0], method_obj)) 

    # Generate update, if any.
    if len(node[2].children) == 1:
        output.extend(expression.gen_expr(info, node[2][0], method_obj))

    output.append('jmp %s' % loop_lbl)

    output.append(end_lbl + ':')

    return output

def gen_while_stmt(info, node, method_obj):
    output = []

    loop_lbl = info.get_jump_label()
    end_lbl = info.get_jump_label()

    output.append(loop_lbl + ':')

    # Generate condition.
    output.extend(expression.gen_expr(info, node[0], method_obj))
    output.append('mov ebx, 0')
    output.append('cmp eax, ebx')
    output.append('je %s' % end_lbl) # If false, go to end.

    # Loop body.
    output.extend(gen_stmt(info, node[1], method_obj))

    output.append('jmp %s' % loop_lbl)

    output.append(end_lbl + ':')

    return output

def gen_empty_stmt(info, node, method_obj):
    return []

def gen_return_stmt(info, node, method_obj):
    output = []

    if len(node.children) != 0:
        output.extend(expression.gen_expr(info, node[0], method_obj))
        pass
    else:
        output.append("mov eax, %d" % 0xDEADBEEF)

    output.append("jmp END~%s" % (method_obj.node.label))

    return output

def gen_static_field_decl(info, node):
    assert node.name == 'FieldDeclaration'
    output = []

    # If there's no initializer, nothing needs to be done. Otherwise, generate
    # the expression code and set it.
    initializer = node[3]
    if len(initializer.children) == 1:
        output.extend(expression.gen_expr(info, initializer[0], None))
        output.append('mov [%s], eax' % node.label)

    return output

