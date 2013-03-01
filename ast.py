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
            typ_imports.append(Node('ImportDeclaration', None, id_list))
        else:
            pkg_imports.append(Node('ImportDeclaration', None, id_list))

        node = node[0]


    # ImportDeclarations => ImportDeclaration
    id_list = flatten(node[0][0][1], 'Name', 'Identifier')

    # Append to appropriate list.
    if node[0][0].name == 'SingleTypeImportDeclaration':
        typ_imports.append(Node('ImportDeclaration', None, id_list))
    else:
        pkg_imports.append(Node('ImportDeclaration', None, id_list))

    typ_imports.reverse()
    pkg_imports.reverse()
    return (typ_imports, pkg_imports)

# Builds the AST for a type declaration. Assumes that the node is a
# ClassDeclaration or a InterfaceDeclaration node.
def build_class_structure(node):
    decl_node = Node('ClassDeclaration')

    # Add modifiers and name (same for classes and interfaces).
    decl_node.add(flatten(node[0], 'Modifiers', 'Modifier'))
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
    decl_node.add(body) # TODO: temporary, remove

    # Extract fields and methods.
    # members = Node('Members')
    members = flatten(node[1], 'Members', 'ClassBodyDeclaration')
    fields = flatten(members, 'Fields', 'FieldDeclaration')
    methods = flatten(members, 'Methods', 'MethodDeclaration')
    classify_methods(methods)

    return decl_node

def build_interface_structure(node):
    decl_node = Node('InterfaceDeclaration')

    # Add modifiers and name (same for classes and interfaces).
    decl_node.add(flatten(node[0], 'Modifiers', 'Modifier'))
    decl_node.add(Node('InterfaceName', None, [node[2]]))

    # Extract interface extends.
    interfaces = Node('Interfaces')
    decl_ints = node.find_child('ExtendsInterfaces')
    if decl_ints is not None:
        interfaces = flatten_interfaces(decl_ints)
    decl_node.add(interfaces)

    members = Node('Members') 

    body = node.find_child('InterfaceBody')
    if body is None:
        logging.error("AST: missing InterfaceBody")
        sys.exit(1)
    decl_node.add(body) # TODO: temporary, remove

    return decl_node

def flatten_interfaces(node):
    interfaces = Node('Interfaces')

    # Find all InterfaceType nodes.
    int_types = flatten(node, 'Interfaces', 'InterfaceType')

    # Flatten each InterfaceType name.
    for int_type in int_types.children:
        interfaces.add(flatten(int_type, 'InterfaceType', 'Identifier'))

    return interfaces

def classify_methods(method_decls):
    constructors = Node('Constructors')
    statics = Node('StaticMethods')
    instance_methods = Node('InstanceMethods')
    
    # for decl in method_decls.children:
    #    method = Node('Method')
    #    method.ad
    # TODO: Finish this

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

# Makes a simple root_name => identifiers structure.
def make_name_node(root_name, identifiers):
    return Node(root_name, None,
        [Node('Identifier', id) for identifier in identifiers])

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

