import typecheck

class CodegenInfo:
    def __init__(self, class_index, type_index):
        self.class_index = class_index
        self.type_index = type_index

        # var_name -> (index, node_decl)
        self.local_vars = {}

        # Counter for local jumps (not exported).
        self.jump_counter = 0

    def get_jump_label(self):
        label = '__jump' + self.jump_counter + ':'
        self.jump_counter += 1
        return label

class FileLayout:
    def __init__(self):
        self.imports = []
        self.exports = []
        self.statics = []
        self.methods = []

def build_exports_list(ast_list):
    pass

# Generates the .s file for the given AST corresponding to a class.
# has_test is True if this was the first file given on the command line.
# This also corresponds to the file that is given the _start symbol.
def gen_asm(node, c_i, t_i, has_test):
    exports = []

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

    output = []

    # Preamble for method.
    label = get_method_label(node)
    output.append("%s:" % label)

    # save ebp & esp
    output.extend([
        "push ebp",
        "mov ebp, esp",
    ])

    # assign frame offsets to each parameter and
    # local variable declaration nodes
    start_index = len(node.find_child('Parameters').children) + 1
    for decl in node.find_child('Parameters'):
        decl.frame_offset = start_index
        start_index -= 1

    start_index = -1
    num_vars = 0
    for decl in find_nodes(Node('LocalVariableDeclaration')):
        decl.frame_offset = start_index
        start_index -= 1
        num_vars += 1

    # make room for local vars in the stack
    output.append("add esp, %d"  (num_vars*4))

    body = node[4] # methodbody or constructorbody
    if len(body.children) != 0:
        output.extend(gen_block(info, body[0], 0))

    # restore ebp & esp
    output.extend([
        "mov esp, ebp",
        "pop ebp"
    ])

    return output

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
        is_static = ''
        if 'static' in node.modifiers:
            is_static = 'STATIC_'

        label = '%sMETHOD%s.%s~@%s' % (is_static, class_name, method_name, param_types)
    return label

