
import environment




def typelink(asts, pkg_index):
    type_index = build_canonical_type_index(pkg_index)
    merge_on_demand_imports(type_index)

    #for t in find_type_nodes(asts):
    #    pass

    weed_single_type_imports(type_index)
    

def find_type_nodes(asts):
    for ast in asts:
        ast.select(['ReferenceType'])


def weed_single_type_imports(type_index):
    """
    - No single-type-import declaration clashes with the class or interface
    declared in the same file.
    - No two single-type-import declarations clash with each other.
    """

    pass

def merge_on_demand_imports(pkg_index):
    """
    given the type_index, which is 
        canonical type name -> compilation unit env of that type

    convert/move the import-on-demands under compulation unit node
    into single-type imports
    """

    pass

def resolve_type(type_index, cu, type_node):
    """
    given a compilation unit and a type, resolve to a canonical name
    if possible, or None.
    """

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
            type_name = environment.type_name(cu)
            if type_name:
                canon_name = '%s.%s' % (pkg_name, type_name)

                if canon_name in type_index:
                    logging.error("No two classes or interfaces have the same canonical name=%s" % canon_name )
                    sys.exit(42)

                type_index[canon_name] = cu
    return type_index
