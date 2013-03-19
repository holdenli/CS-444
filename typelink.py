
import sys

import environment

from utils import logging
from utils.node import Node

from utils.node import find_nodes

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
            imports = cu_env['TypeImport']
            if imports:
                imports = set(imports.names)
            else:
                imports = set()

            for i in imports:
                if i not in type_index:
                    logging.error("Type import '%s' could not be resolved" % i)
                    sys.exit(42)

            # then, we find type references and resolve those
            for type_node in find_type_nodes(cu_env):
                array_parent = None
                if type_node[0] == Node('ArrayType'):
                    array_parent = type_node
                    type_node = type_node[0]

                if type_node[0] == Node('PrimitiveType'):
                    type_node.canon = type_node[0][0].name

                elif type_node[0] == Node('Void'):
                    type_node.canon = 'Void'

                elif type_node[0] == Node('ReferenceType'):
                    ref_type_node = type_node[0]

                    canon_name = resolve_type(type_index, cu_env, pkg_name,
                        ref_type_node)

                    if canon_name == None:
                        type_name = ref_type_node.select_leaf_values(['Identifier'])[0]
                        logging.error('Cant type link "%s"' % type_name)
                        sys.exit(42)

                    # lets link the type node to its compilation unit
                    type_node.env = type_index[canon_name]
                    type_node.canon = canon_name

                if array_parent != None:
                    array_parent.env = type_node.env
                    array_parent.canon = type_node.canon + "[]"

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

    type_name = '.'.join(type_node.leaf_values())

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
    imports = cu_env['TypeImport']
    if imports:
        imports = set(imports.names)
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
    for node in n.select(['Type']):
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
