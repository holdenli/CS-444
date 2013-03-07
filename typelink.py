
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

    for pkg in pkg_index.values():
        for e in pkg:
            #merge_on_demand_imports(e, type_index, pkg_index)
            pass

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

    type_name = '.'.join(l.value.value for l in type_node.leafs())

    # maybe it's fully qualified?
    if type_name in type_index:
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
