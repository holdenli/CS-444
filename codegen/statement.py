from codegen import expression

#
# Codegen for expressions.
#

def gen_block(info, node):

    # generate local variables for this block
    for i, (var_name, var_decl) in enumerate(node.env.names.items()):
        info.local_vars[var_name] = (i, var_decl)

    for stmt in node.children:
        if stmt.name == 'LocalVariableDeclaration':
            pass
        elif stmt.name == 'Block':
            gen_block(info, stmt)
        elif stmt.name == 'ExpressionStatement':
            gen_expr_stmt(info, stmt)

def gen_expr_stmt(info, stmt):

    output = []

    output.extend(expression.gen_expr(info, n[0]))

    return output

def gen_if_stmt(info, node):
    output = []
    return output

def gen_for_stmt(info, node):
    output = []
    return output

def gen_while_stmt(info, node):
    output = []
    return output

def gen_empty_stmt(info, node):
    return []

def gen_local_variable_decl(info, node):
    output = []
    return output

def gen_return_stmt(info, node):
    output = []
    return output

def gen_static_field_decl(info, node):
    assert node.name == 'FieldDeclaration'
    output = []

    # If there's no initializer, nothing needs to be done. Otherwise, generate
    # the expression code and set it.
    initializer = node[3]
    if len(initializer.children) == 1:
        output.extend(expression.gen_expr(info, initializer[0]))
        output.append('mov [%s], eax' % node.label)

    return output

