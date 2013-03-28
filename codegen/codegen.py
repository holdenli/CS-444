
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

    if n[0].name == 'Assignment':
        output.extend(gen_assignment_expr(info, n[0]))

    elif n[0].name == 'MethodInvocation':
        output.extend(gen_method_invocation(info, n[0]))
        pass

    elif n[0].name == 'ClassInstanceCreationExpression':
        pass

    return output

def gen_assignment_expr(info, node):
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
        output.append("dd %s" % node[0].value == 'true')

    elif node[0].name == 'CharacterLiteral':
        output.append("dd %s" % node[0].value) # .value = "'c'"

    elif node[0].name == 'StringLiteral':
        # make a string object
        pass
    
    elif node[0].name == 'NullLiteral':
        # how to handle this?
        pass

    return output

def gen_method_invocation(info, node):
    pass 

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
