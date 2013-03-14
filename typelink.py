
import sys

import environment

from utils import logging
from utils.node import Node

def typelink(asts, pkg_index):
    type_index = build_canonical_type_index(pkg_index)

    # prefix checks
    prefixes = list(type_index.keys()) + list(pkg_index.keys())
    for t in type_index:
        for x in prefixes:
            if len(x) == len(t):
                continue
            elif x.startswith(t):
                if (x[len(t)] == "."):
                    logging.error('"%s" is a prefix of "%s"' % (t, x))
                    sys.exit(42)

    weed_single_type_imports(type_index, pkg_index)

    for pkg_name in pkg_index:
        for cu_env in pkg_index[pkg_name]:

            # first, we resolve the type imports
            imports = list(cu_env.select(['CompilationUnit', 'TypeImport']))
            if imports:
                imports = set(imports[0].names)
            else:
                imports = set()

            for i in imports:
                if i not in type_index:
                    logging.error("Type import '%s' could not be resolved" % i)
                    sys.exit(42)

            # then, we find type references and resolve those
            for type_node in find_type_nodes(cu_env):
                canon_name = resolve_type(type_index, cu_env, pkg_name, type_node)
                if canon_name == None:
                    type_name = type_node.select_leaf_values(['Identifier'])[0]
                    logging.error('Cant type link "%s"' % type_name)
                    sys.exit(42)

                # lets link the type node to its compilation unit
                type_node.env = type_index[canon_name]

    name_link(pkg_index, type_index)

    return type_index

def resolve_type(type_index, cu_env, pkg_name, type_node):
    """
    given a compilation unit, the package it's in,
    and a type node, resolve to a canonical type name

    pkg_name is a string (e.g., 'java.lang')
    type_node is ASTNode
    cu_env is Environment
    type_index is a dict of canonical type names -> Environment of compilation
    unit
    """

    type_name = '.'.join(l.value.value for l in type_node.leafs())

    return resolve_type_by_name(type_index, cu_env, pkg_name, type_name)

def resolve_type_by_name(type_index, cu_env, pkg_name, type_name):

    # maybe it's fully qualified?
    if type_name in type_index:
        # check that no prefixes of fully qualified types themselves resolve to
        # types!
        type_prefix = type_name.rsplit('.', 1)[0]
        if resolve_type_by_name(type_index, cu_env, pkg_name, type_prefix) != None:
            logging.error('Prefix "%s" of type "%s" also resolves to a type' \
                % (type_prefix, type_name))
            sys.exit(42)

        return type_name
   
    # build a list of imports in this CU
    imports = list(cu_env.select(['CompilationUnit', 'TypeImport']))
    if imports:
        imports = set(imports[0].names)
    else:
        imports = set()

    # is it a local type?
    if environment.env_type_name(cu_env) == type_name:
        return '%s.%s' % (pkg_name, environment.env_type_name(cu_env))

    # is it one of the imports?
    candidates = set()
    for i in imports:
        i_pkg = '.'.join(i.split('.')[:-1])
        canon_type = '%s.%s' % (i_pkg, type_name)
        if canon_type in imports:
            candidates.add(canon_type)

    if len(candidates) == 1:
        return candidates.pop()
    elif len(candidates) > 1:
        logging.error('Could not resolve type %s; candidates: %s' % (type_name,
            candidates))
        sys.exit(42)

    # is it in the same package?
    canon_type = '%s.%s' % (pkg_name, type_name)
    if canon_type in type_index:
        return canon_type

    # is it an an ondemand package?
    candidates = set()
    on_demands = list(cu_env.select(['CompilationUnit', 'PackageImports']))[0].names
    on_demands['java.lang'] = Node('JAVA.LANG.PACKAGE')

    if len(on_demands) != 0:
        for i in on_demands:
            canon_type = '%s.%s' % (i, type_name)
            if canon_type in type_index:
                candidates.add(canon_type)

    if len(candidates) == 1:
        return candidates.pop()
    elif len(candidates) > 1:
        logging.error('Could not resolve type %s; candidates: %s' % (type_name,
            candidates))
        sys.exit(42)

    return None
    
def find_type_nodes(cu_env):
    n = environment.env_type_node(cu_env)
    for node in n.select(['ReferenceType']):
        yield node

def weed_single_type_imports(type_index, pkg_index):
    """
    - No single-type-import declaration clashes with the class or interface
    declared in the same file.
    - No two single-type-import declarations clash with each other.
    """
    for type_name in type_index:
        cu = type_index[type_name]
        pkg_imports = cu.find_child("PackageImports")
        if pkg_imports != None:
            for pkg_imp in pkg_imports.names:

                found = False
                for valid_pkg in pkg_index:
                    if valid_pkg == pkg_imp or valid_pkg.startswith(pkg_imp+'.'):
                        found = True
                        break

                if found == False:
                    logging.error("Package import %s doesnt exist" % pkg_imp)
                    sys.exit(42)

    for canon_type in type_index:
        cu = type_index[canon_type]
        type_name = environment.env_type_name(cu)

        ti = list(cu.select(['TypeImport']))[0]
        for ti_name in ti.names:
            if ti_name.endswith('.'+type_name) and \
                ti_name != canon_type:

                logging.error("No single-type-import declaration clashes with the class or interface declared in the same file; type name=%s" % type_name)
                sys.exit(42)

        if len(set(name.split('.')[-1] for name in ti.names)) != \
            len(ti.names):
            logging.error("Two single-type-import declarations must not clash with each other")
            sys.exit(42)

def build_canonical_type_index(pkg_index):
    """
    returns a dictionary of
        canonical typename -> compilation unit Env

    given the package index (which is returned by environment.build_environment())
    """
    type_index = {}
    for pkg_name in pkg_index:
        for cu in pkg_index[pkg_name]:

            # get canonical name of the type from this compilation unit
            type_name = environment.env_type_name(cu)
            if type_name:
                canon_name = '%s.%s' % (pkg_name, type_name)

                if canon_name in type_index:
                    logging.error("No two classes or interfaces have the same canonical name=%s" % canon_name )
                    sys.exit(42)

                type_index[canon_name] = cu
    return type_index

def name_link(pkg_index, type_index):
    for pkg_name in pkg_index:
        for cu_env in pkg_index[pkg_name]:
            if cu_env['ClassDeclaration'] == None:
                continue

            typedecl_env = cu_env['ClassDeclaration']
            for method_name in typedecl_env.methods:
                for method_node in typedecl_env.methods[method_name]:
                    for block_node in method_node.select(['Block']):
                        name_link_block(type_index, cu_env, pkg_name, block_node,
                            local_vars=environment.build_method_params(method_node))

def name_link_block(type_index, cu_env, pkg_name, stmts, local_vars=None):
    if local_vars == None:
        local_vars = {}

    local_vars = dict(local_vars)

    for stmt in stmts.children:
        if stmt == Node('Block'):
            name_link_block(type_index, cu_env, pkg_name, stmt, local_vars)
            continue

        elif stmt == Node('ForStatement'):
            # stmt.children = [ForInit, ForCondition, ForUpdate, ForBody]
            for_vars = list(stmt.select(['ForStatement', 'ForInit',
                'LocalVariableDeclaration']))

            if len(for_vars) != 0:
                var_name = for_vars[0][1].value.value
                local_vars[var_name] = for_vars[0]

            find_and_resolve_names(type_index, cu_env, pkg_name, stmt[0],
                local_vars)
            find_and_resolve_names(type_index, cu_env, pkg_name, stmt[1],
                local_vars)
            find_and_resolve_names(type_index, cu_env, pkg_name, stmt[2],
                local_vars)
            
            for block_stmt in stmt[3].select(['Block']):
                name_link_block(type_index, cu_env, pkg_name, block_stmt, local_vars)
            continue

        elif stmt == Node('WhileStatement'):
            find_and_resolve_names(type_index, cu_env, pkg_name, stmt[0],
                local_vars)

            name_link_block(type_index, cu_env, pkg_name, stmt[1], local_vars)
            continue

        elif stmt == Node('IfStatement'):

            find_and_resolve_names(type_index, cu_env, pkg_name, stmt[0],
                local_vars)

            name_link_block(type_index, cu_env, pkg_name, stmt[1], local_vars)
            if len(stmt.children) == 3:
                name_link_block(type_index, cu_env, pkg_name, stmt[2], local_vars)
            continue

        if stmt == Node('LocalVariableDeclaration'):
            var_name = list(stmt.select(['LocalVariableDeclaration', 'Identifier']))
            var_name = var_name[0].value.value
            local_vars[var_name] = stmt

        # find name references
        find_and_resolve_names(type_index, cu_env, pkg_name, stmt, local_vars)

def find_and_resolve_names(type_index, cu_env, pkg_name, stmt, local_vars):
    for name_node in stmt.select(['Name']):
        name = name_node.leaf_values()
        resolved_node = name_link_name(type_index, cu_env, pkg_name, local_vars, '.'.join(name))

        if resolved_node == None:
            logging.error('Could not resolve name %s in %s.%s with %s' % (name, pkg_name,
                cu_env['ClassDeclaration'], local_vars))
            sys.exit(42)

def name_link_name(type_index, cu_env, pkg_name, local_vars, name):

    def find_field(typedecl_env, name):
        if name in typedecl_env.fields:
            return typedecl_env.fields[name]

        if name in typedecl_env.methods:
            return typedecl_env.methods[name]

        # lets check the parent class instead
        super_node = typedecl_env.node.find_child('Superclass')
        if super_node.children:
            super_env = list(super_node.select(['ReferenceType']))[0].env
            return find_field(super_env['ClassDeclaration'], name)

        return None

    name_parts = name.split('.')
    
    typedecl_env = cu_env['ClassDeclaration'] or cu_env['InterfaceDeclaration']
    if name_parts[0] in local_vars:
        return local_vars[name_parts[0]]

    r = find_field(typedecl_env, name_parts[0])
    if r:
        return r

    # maybe it's a type?
    for i, _ in enumerate(name_parts):
        canon_name = resolve_type_by_name(type_index, cu_env, pkg_name,
                                            '.'.join(name_parts[:i+1]))

        if canon_name:
            return environment.env_type_name(type_index[canon_name])

    return None
   
