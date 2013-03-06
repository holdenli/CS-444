
import environment

def typelink(asts, pkg_index):
    
    for pkg_name in pkg_index:
        for cu in pkg_index[pkg_name]:
            type_name = environment.type_name(cu)

            # get canonical name of the type from this compilation unit
            type_env = pkg_env.children[0].children[2]
            type_name = type_env.value
            canon_name = '%s.%s' % (pkg_name, type_name)

            if canon_name in type_index:
                logging.error("No two classes or interfaces have the same canonical name=%s" % canon_name )
                sys.exit(42)
            type_index[canon_name] = type_env
            
