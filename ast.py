#!/usr/bin/python3

from utils import logging
from utils.node import Node

# Processes the provide parse tree (root) node and returns the root ASTNode
# of the abstract syntax tree of the input.
# This is destructive - parse_tree should not be used afterwards.
def build_ast(parse_tree):
    ast = Node('Root')
    
    # Start with CompilationUnit.
    unit = parse_tree.find_child('CompilationUnit')
    if unit is not None:
        cu = Node('CompilationUnit')
        ast.add(build_top_level(Node('CompilationUnit'), unit))

    return ast

# Given the AST node of a Compilation Unit being constructed, and the
# CompilationUnit node of a parse tree, determine the top-level structure
# of the AST.
def build_top_level(ast, unit):
    # Extract package declaration, if it exists.
    pkg = Node('PackageDeclaration')
    package_decl = unit.find_child('PackageDeclaration')
    if package_decl is not None:
        #pkg.children = flatten_name(package_decl[1])
        pkg = flatten(package_decl[1], 'PackageDeclaration', 'Identifier')
    ast.add(pkg)

    # Extract imports, if they exist.
    typ_imports = Node('TypeImports')
    pkg_imports = Node('PackageImports')
    import_decl = unit.find_child('ImportDeclarations')
    if import_decl is not None:
        typ_imports.children, pkg_imports.children = flatten_imports(import_decl)
    ast.add(typ_imports)
    ast.add(pkg_imports)

    # Extract type declaration.
    typ_decl = unit.find_child('TypeDeclarations')
    if typ_decl is not None and typ_decl[0][0].name != 'SemiColon':
        if typ_decl[0][0].name == 'ClassDeclaration':
            typ = build_class_structure(typ_decl[0][0])
        elif typ_decl[0][0].name == 'InterfaceDeclaration':
            typ = build_interface_structure(typ_decl[0][0])
        ast.add(typ)

    return ast

# Helper for flattening import declarations.
def flatten_imports(node):
    typ_imports = []
    pkg_imports = []

    while node.first.name != 'ImportDeclaration':

        # ImportDeclarations => ImportDeclarations ImportDeclaration
        id_list = flatten(node[1][0][1], 'Name', 'Identifier')

        # Append to appropriate list.
        if node[1][0].name == 'SingleTypeImportDeclaration':
            typ_imports.append(Node('ImportDeclaration', None, id_list.children))
        else:
            pkg_imports.append(Node('ImportDeclaration', None, id_list.children))

        node = node[0]


    # ImportDeclarations => ImportDeclaration
    id_list = flatten(node[0][0][1], 'Name', 'Identifier')

    # Append to appropriate list.
    if node[0][0].name == 'SingleTypeImportDeclaration':
        typ_imports.append(Node('ImportDeclaration', None, id_list.children))
    else:
        pkg_imports.append(Node('ImportDeclaration', None, id_list.children))

    typ_imports.reverse()
    pkg_imports.reverse()
    return (typ_imports, pkg_imports)

# Builds the AST node for a type declaration. Assumes that the node is a
# ClassDeclaration.
def build_class_structure(node):
    decl_node = Node('ClassDeclaration')

    # Add modifiers and name (same for classes and interfaces).
    decl_node.add(flatten_leaves(node[0], 'Modifiers'))
    decl_node.add(Node('ClassName', None, [node[2]]))

    # Extract superclass.
    superstuff = node.find_child('SuperStuff')
    if superstuff is None: # No extends, so extend java.lang.Object
        decl_node.add(Node('Superclass')) # empty for now
    #     decl_node.add(make_name_node('Superclass', ["java", "lang", "Object"]))
    else:
        decl_node.add(flatten(superstuff, 'Superclass', 'Identifier'))

    # Extract interface implements.
    interfaces = Node('Interfaces')
    decl_ints = node.find_child('Interfaces')
    if decl_ints is not None:
        interfaces = flatten_interfaces(decl_ints)
    decl_node.add(interfaces)

    body = node.find_child('ClassBody')
    if body is None:
        logging.error("AST: missing ClassBody")
        sys.exit(1)

    # Extract fields, constructors, and methods.
    members = flatten(body, 'Members', 'ClassBodyDeclaration')
    fields = flatten(members, 'Fields', 'FieldDeclaration')
    decl_node.add(build_fields(fields))
    constructors = flatten(members, 'Constructors', 'ConstructorDeclaration')
    decl_node.add(build_constructors(constructors))
    methods = flatten(members, 'Methods', 'MethodDeclaration')
    decl_node.add(build_methods(methods))

    return decl_node

# Returns a processed Fields AST node for the input Fields node.
def build_fields(node):
    fields = Node('Fields')
    for field_decl in node.children:
        field = Node('FieldDeclaration')

        # Extract modifiers.
        field.add(flatten_leaves(field_decl[0], 'Modifiers'))

        # Extract type.
        field.add(build_type(field_decl[1]))

        # Extract name.
        field.add(field_decl[2][0][0][0])

        # Extract initializer.
        var_declr = field_decl[2][0] # VariableDeclarator
        if len(var_declr.children) > 1:
            initializer = build_expr(var_declr[2][0])
            field.add(Node('Initializer', None, [initializer]))
        else:
            field.add(Node('Initializer')) # No initializer

        fields.add(field)

    return fields

def build_constructors(node):
    constructors = Node('Constructors')
    for cons_decl in node.children:
        cons = Node('ConstructorDeclaration')

        # Extract modifiers.
        cons.add(flatten_leaves(cons_decl[0], 'Modifiers'))

        # Extract name.
        cons.add(cons_decl[1][0][0]) # Name

        # Extract parameters.
        if cons_decl[1][2] == 'FormalParameterList':
            cons.add(build_parameters(cons_decl[1][2]))
        else:
            cons.add(Node('Parameters'))

        # Extract body.
        if cons_decl[2][1].name == 'BlockStatements':
            cons.add(build_block(cons_decl[2][1]))
        else:
            cons.add(Node('Block'))

        constructors.add(cons)

    return constructors

def build_methods(node):
    methods = Node('Methods')
    for method_decl in node.children:
        method = Node('MethodDeclaration')

        # Extract modifiers.
        method.add(flatten_leaves(method_decl[0][0], 'Modifiers'))

        # Extract return type.
        if method_decl[0][1].name == 'Void':
            method.add(Node('Type', None, [method_decl[0][1]]))
        else:
            method.add(build_type(method_decl[0][1])) # Non-void.

        # Name.
        method.add(method_decl[0][2][0])
 
        # Extract parameters.
        if method_decl[0][2][2].name == 'FormalParameterList':
            method.add(build_parameters(method_decl[0][2][2]))
        else:
            method.add(Node('Parameters'))

        # Extract body.
        # We have two levels, for differentiating between:
        # 1. Methods with no body (i.e., abstract)
        # 2. Methods with an empty body (i.e., {})
        # 3. Methods with a nonempty body
        body = Node('MethodBody')
        if method_decl[1].name != 'SemiColon' and \
                method_decl[1][0].name != 'SemiColon':
            blk = method_decl[1][0]
            if blk[1].name == 'BlockStatements':
                body.add(build_block(blk[1]))
            else:
                body.add(Node('Block'))
        method.add(body)

        methods.add(method)

    return methods        

# Returns a processed Type node.
def build_type(node):
    typ = Node('Type')
    # return node
    if node[0].name == 'PrimitiveType':
        typ.add(flatten_leaves(node[0], 'PrimitiveType'))
    elif node[0][0].name == 'ClassOrInterfaceType':
        typ.add(flatten(node[0][0], 'ReferenceType', 'Identifier'))
    elif node[0][0][0].name == 'PrimitiveType': # ArrayType of PrimitiveType
        typ.add(Node('ArrayType', None,
            [flatten_leaves(node[0][0][0], 'PrimitiveType')]))
    else: # ArrayType of ClassOrInterfaceType
        typ.add(Node('ArrayType', None,
            [flatten(node[0][0][0], 'ReferenceType', 'Identifier')]))

    return typ

# Returns a processed Parameters node, given a FormalParameterList node of the
# parse tree.
def build_parameters(node):
    params = Node('Parameters')

    # Get a list of FormalParameter.
    param_decls = flatten(node, 'Parameters', 'FormalParameter')
    for param_decl in param_decls.children:
        param = Node('Parameter')
        param.add(build_type(param_decl[0]))
        param.add(param_decl[1][0]) # Name

        params.add(param)

    return params

# Builds the AST node for an interface declaration. node must be an
# InterfaceDeclaration.
def build_interface_structure(node):
    decl_node = Node('InterfaceDeclaration')

    # Add modifiers and name (same for classes and interfaces).
    decl_node.add(flatten_leaves(node[0], 'Modifiers'))
    decl_node.add(Node('InterfaceName', None, [node[2]]))

    # Extract interface extends.
    interfaces = Node('Interfaces')
    decl_ints = node.find_child('ExtendsInterfaces')
    if decl_ints is not None:
        interfaces = flatten_interfaces(decl_ints)
    decl_node.add(interfaces)

    body = node.find_child('InterfaceBody')
    if body is None:
        logging.error("AST: missing InterfaceBody")
        sys.exit(1)

    # Joos only allows methods to be in interfaces.
    methods = flatten(body, 'Methods', 'InterfaceMemberDeclaration')
    decl_node.add(build_methods(methods)) 

    return decl_node

def build_expr(node):
    return node

def build_block(node):
    return node

def flatten_interfaces(node):
    interfaces = Node('Interfaces')

    # Find all InterfaceType nodes.
    int_types = flatten(node, 'Interfaces', 'InterfaceType')

    # Flatten each InterfaceType name.
    for int_type in int_types.children:
        interfaces.add(flatten(int_type, 'InterfaceType', 'Identifier'))

    return interfaces

# Given a node, find all occurrences of leaf_name and returns a node with
# root_name with all occurrences of leaf_name in node as its children.
# Children are in-order.
def flatten(node, root_name, leaf_name):
    root = Node(root_name)
    stack = [node]

    while len(stack) > 0:
        n = stack.pop()
        if n.name == leaf_name:
            root.add(n)
        else:
            stack.extend(n.children)

    root.children.reverse()

    return root

# Given a node, find all the leaves in-order, and returns them as children of
# a node node with name root_name.
def flatten_leaves(node, root_name):
    root = Node(root_name)
    stack = node.children
    
    while len(stack) > 0:
        n = stack.pop()
        if len(n.children) == 0:
            root.add(n)
        else:
            stack.extend(n.children)

    root.children.reverse()

    return root

# Makes a simple root_name => identifiers structure.
def make_name_node(root_name, identifiers):
    return Node(root_name, None,
        [Node('Identifier', id) for identifier in identifiers])

###############################################################################

# Convenience functions

# Returns a string of the qualified name of a node
# This assume it has a list of identifiers as children
def get_qualified_name(node):
    s = ""
    if node == None:
        return ""
    for i in node.children:
        s += "." + i.value.value
    return s[1:]

def get_type(node):
    if node.find_child("ArrayType") == None:
        return node.leafs()[0].value.value
    else:
        return node.leafs()[0].value.value + "[]"

def get_modifiers(node):
    if node == None:
        return []
    m = []
    for i in node.children:
        m.append(i.name)
    return m

def get_parameters(node):
    if node == None:
        return []
    p = []
    for i in node.children:
        p.append(get_type(i.find_child("Type")))
    return p

#################################### Unused ###################################

def collapse(node):

    def collapse_rec(node):
        """
        recursive helper function for collapsing nodes
        """
        if type(node) is not Node:
            return

        newchildren = []
        for c in node.children:
            if c == node:
                collapse(c)
                newchildren.extend(c.children)
            else:
                newchildren.append(c)

        node.children = newchildren 

    """
    collapse nodes generated from one-or-more style grammar rules such as

    Rule=[Rule=[Rule=[Terminal] Terminal] Terminal] 

    to Rule=[Terminal, Terminal, Terminal]
    """
    # collapse breadth-first-search style
    nodes = [parse_tree]
    for node in nodes:
         collapse_rec(node)
         nodes.extend(node.children)


class ASTNode(Node):
    pass 

