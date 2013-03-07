
import sys

import environment

from utils import logging

def typelink(asts, pkg_index):
    type_index = build_canonical_type_index(pkg_index)

    weed_single_type_imports(type_index)

    for pkg in pkg_index.values():
        for e in pkg:
            merge_on_demand_imports(e, type_index, pkg_index)

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
                r = resolve_type(type_index, cu_env, pkg_name, type_node)
                if r == None:
                    type_name = type_node.select_leaf_values(['Identifier'])[0]
                    logging.error('Cant type link "%s"' % type_name)
                    sys.exit(42)


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

    # build a list of imports in this CU
    imports = list(cu_env.select(['CompilationUnit', 'TypeImport']))
    if imports:
        imports = set(imports[0].names)
    else:
        imports = set()

    # the local type is also in the imports!
    imports.add('%s.%s' % (pkg_name, environment.env_type_name(cu_env)))

    # now we resolve type_name to something canonical.
    # is it one of the imports?
    type_name = '.'.join(l.value.value for l in type_node.leafs())
    for i in imports:
        i_pkg = '.'.join(i.split('.')[:-1])
        canon_type = '%s.%s' % (i_pkg, type_name)
        if canon_type in imports:
            return canon_type

    # maybe it's java.lang?
    if 'java.lang.%s' % type_name in type_index:
        return 'java.lang.%s' % type_name
    
    # maybe it's fully qualified?
    if type_name in type_index:
        return type_name

    return None

def find_type_nodes(cu_env):
    n = environment.env_type_node(cu_env)
    for node in n.select(['ReferenceType']):
        yield node

def weed_single_type_imports(type_index):
    """
    - No single-type-import declaration clashes with the class or interface
    declared in the same file.
    - No two single-type-import declarations clash with each other.
    """

    for canon_type in type_index:
        cu = type_index[canon_type]
        type_name = environment.env_type_name(cu)   

        ti = list(cu.select(['TypeImport']))[0]

        if sum([k.endswith('.'+type_name) for k in ti.names]) > 0:
            logging.error("No single-type-import declaration clashes with the class or interface declared in the same file; type name=%s" %
            type_name)

            sys.exit(42)

        if len(set(name.split('.')[-1] for name in ti.names)) != \
            len(ti.names):
            logging.error("Two single-type-import declarations must not clash with each other")
            sys.exit(42)

def merge_on_demand_imports(cu, type_index, pkg_index):
    """
    given the env compulation unit, type index, and package index

    convert/move the import-on-demands under compulation unit node
    into single-type imports
    """

    pkg_imports = cu.find_child("PackageImports")
    if pkg_imports == None:
        return

    for pkg_name in pkg_imports.names:
        for type_name in [t for t in type_index if t.startswith(pkg_name+'.')]:
            if '.' not in type_name[len(pkg_name)+1:]:
                cu.find_child("TypeImport").names[type_name] = pkg_imports.names[pkg_name]

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
