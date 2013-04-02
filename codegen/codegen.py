
class CodegenInfo:
    def __init__(self, class_index, type_index):
        self.class_index = class_index
        self.type_index = type_index

        # var_name -> (index, node_decl)
        self.local_vars = {}


def lookup_by_decl(vars_dict, item):
    for (var_name, (i, var_decl)) in node.env.names.items():
        if item.obj == var_decl.obj and item.obj != None:
            return var_name

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

    output.extend(gen_expr(info, n[0]))

    return output

def gen_method(info, node):
    assert node.name in ['MethodDeclaration', 'ConstructorDeclaration']

    # Preamble for method.
    code = get_method_label(node)

    body = node[4]
    if len(body.children) != 0:
        code += gen_block(info, body[0], 0)

def get_method_label(node):
    assert node.name in ['MethodDeclaration', 'ConstructorDeclaration']

    # Special case for native methods.
    # TODO: "in Joos 1W, all native methods must be static, must take a single
    # argument of type int, and must return a value of type int" should be
    # checked.

    label = ''
    class_name = node.obj.declared_in.name
    method_name = node.obj.name
    parameters = node[3]
    param_types = []
    for param in parameters:
        if typecheck.is_array_type(param[0].canon) == True:
            param_types.append(param[0].canon[:-2] + '@') # chop off the []
        else:
            param_types.append(param[0].canon)
    if 'native' in node.modifiers: 
        label = 'NATIVE%s.%s' % (class_name, method_name)
    else:
        label = 'METHOD%s.%~@%s:' % (class_name, method_name, param_types)
    return label

