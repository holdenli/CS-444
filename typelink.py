
import sys

import environment

from utils import logging

def typelink(asts, pkg_index):
    type_index = build_canonical_type_index(pkg_index)

    #asts[0][0].pprint()
    """
    print(pkg_index)
    for pkg in pkg_index.values():
        for e in pkg:
            merge_on_demand_imports(e, type_index, pkg_index)
    """

    for pkg_name in pkg_index:
        for cu_env in pkg_index[pkg_name]:
            for type_node in find_type_nodes(cu_env):
                r = resolve_type(type_index, cu_env, pkg_name, type_node)
                if r == None:
                    logging.error('Cant type link')
                    sys.exit(42)

    weed_single_type_imports(type_index)

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

    type_name = '.'.join(l.value.value for l in type_node.leafs())

    # now we resolve type_name to something canonical.
    # is it one of the imports?
    for i in imports:
        i_pkg = '.'.join(i.split('.')[:-1])
        canon_type = '%s.%s' % (i_pkg, type_name)
        if canon_type in imports:
            return canon_type

    # maybe it's java.lang?
    if 'java.lang.%s' % type_name in type_index:
        return 'java.lang.%s' % type_name

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

    pass

def merge_on_demand_imports(cu, type_index, pkg_index):
    """
    given the env compulation unit, type index, and package index

    convert/move the import-on-demands under compulation unit node
    into single-type imports
    """

    print("####")
    cu.pprint()

    imports_node = cu.find_child("PackageImports")
    if imports_node == None:
        return cu

    print("-- on demand imports: --")
    for n in imports_node.names.keys():
        print(n)
        for t in [x for x in type_index.keys() if x.startswith(n)]:
            print("  ", t)

    pass

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
