#!/usr/bin/python3

from utils import logging
from utils.node import Node

# Processes the provide parse tree (root) node and returns the root ASTNode
# of the abstract syntax tree of the input.
# This is destructive - parse_tree should not be used afterwards.
def build_ast(parse_tree):
    
    # Start with CompilationUnit.
    unit = parse_tree.find_child('CompilationUnit')
    if unit is None:
        return None
    else:
        ast = Node('CompilationUnit')
        return build_top_level(ast, unit)

# Given the AST node of a Compilation Unit being constructed, and the
# CompilationUnit node of a parse tree, determine the top-level structure
# of the AST.
def build_top_level(ast, unit):

    # Extract package declaration, if it exists.
    pkg = Node('PackageDeclaration')
    package_decl = unit.find_child('PackageDeclaration')
    if package_decl is not None:
        pkg.children = flatten_name(package_decl[1])
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
        typ = build_type_structure(typ_decl[0])
        ast.add(typ)

    return ast

# Given a Name parse tree node, return a list of all the Identifiers.
# Essentially, given a Name (possibly qualified) that was parsed in the form
# a.b.c.d, this returns a list [a, b, c, d] of Identifiers.
def flatten_name(node):
    id_list = []

    while node.first.name != 'SimpleName':
        # Name => QualifiedName => Name Dot Identifier
        id_list.append(node[0][2]) # Get the Identifier.
        node = node[0][0] # Continue on Name.

    # Name => SimpleName => Identifier
    id_list.append(node[0][0]) # Get the final Identifier.

    id_list.reverse()
    return id_list

def flatten_imports(node):
    typ_imports = []
    pkg_imports = []

    while node.first.name != 'ImportDeclaration':

        # ImportDeclarations => ImportDeclarations ImportDeclaration
        id_list = flatten_name(node[1][0][1]) # Same for typ and pkg imports.

        # Append to appropriate list.
        if node[1][0].name == 'SingleTypeImportDeclaration':
            typ_imports.append(Node('ImportDeclaration', None, id_list))
        else:
            pkg_imports.append(Node('ImportDeclaration', None, id_list))

        node = node[0]


    # ImportDeclarations => ImportDeclaration
    id_list = flatten_name(node[0][0][1]) # Same for typ and pkg imports.

    # Append to appropriate list.
    if node[0][0].name == 'SingleTypeImportDeclaration':
        typ_imports.append(Node('ImportDeclaration', None, id_list))
    else:
        pkg_imports.append(Node('ImportDecalration', None, id_list))

    typ_imports.reverse()
    pkg_imports.reverse()
    return (typ_imports, pkg_imports)

def build_type_structure(node):
    return node # TODO

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

