import sys

from utils import logging

from codegen import expression

#
# Codegen for statements.
#

def gen_stmt(info, node, method_obj):
    if node.name == 'LocalVariableDeclaration':
        logging.warning("gen_stmt: %s" % node)
        return []
    elif node.name == 'Block':
        return gen_block(info, node)
    elif node.name == 'ExpressionStatement':
        return gen_expr_stmt(info, node, method_obj)
    elif node.name == 'ReturnStatement':
        logging.warning("gen_stmt: %s" % node)
        return []
    elif node.name == 'IfStatement':
        logging.warning("gen_stmt: %s" % node)
        return []
    elif node.name == 'WhileStatement':
        logging.warning("gen_stmt: %s" % node)
        return []
    elif node.name == 'ForStatement':
        logging.warning("gen_stmt: %s" % node)
        return []


    # Bad.
    else:
        logging.error('FATAL ERROR: Invalid node %s for gen_block()' %
            node.name)
        sys.exit(1)

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
    return output

def gen_for_stmt(info, node, method_obj):
    output = []
    return output

def gen_while_stmt(info, node, method_obj):
    output = []
    return output

def gen_empty_stmt(info, node, method_obj):
    return []

def gen_local_variable_decl(info, node, method_obj):
    output = []
    return output

def gen_return_stmt(info, node, method_obj):
    output = []
    return output

def gen_static_field_decl(info, node, method_obj):
    assert node.name == 'FieldDeclaration'
    output = []

    # If there's no initializer, nothing needs to be done. Otherwise, generate
    # the expression code and set it.
    initializer = node[3]
    if len(initializer.children) == 1:
        output.extend(expression.gen_expr(info, initializer[0]))
        output.append('mov [%s], eax' % node.label)

    return output

