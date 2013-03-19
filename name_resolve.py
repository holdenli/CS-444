
import sys

from utils import logging
from utils import primitives

from utils.node import Node
from utils.node import ASTNode
from utils.node import find_nodes
import environment

from typelink import resolve_type_by_name

import utils.class_hierarchy 
from utils.class_hierarchy import Temp_Field, Temp_Method, Temp_Constructor
from utils.class_hierarchy import is_nonstrict_subclass

class_index = {}

static_context_flag = False

def name_link(pkg_index, type_index, cls_idx):
    global class_index
    global static_context_flag
    static_context_flag = False

    class_index = cls_idx

    for pkg_name in pkg_index:
        for cu_env in pkg_index[pkg_name]:
            if cu_env['ClassDeclaration'] == None:
                continue

            typedecl_env = cu_env['ClassDeclaration']

            # name link everything inside methods!
            for method_env in typedecl_env.children:
                method_node = method_env.node
                static_context_flag = 'static' in method_node.modifiers

                for block_node in method_node.select(['Block']):
                    
                    name_link_block(type_index, cu_env, pkg_name, block_node,
                            local_vars=environment.build_method_params(method_node))

                    if len(list(method_node.select(['This']))) > 0 and \
                        'static' in method_node.modifiers:

                        logging.error("Cannot use 'this' inside static method")
                        sys.exit(42)

                static_context_flag = False

            # name link field initializers
            all_fields = typedecl_env.node.select(['Fields', 'FieldDeclaration'])
            all_fields = [f.find_child('Identifier').value.value for f in all_fields]

            disallowed = set(f for f in all_fields)
            fields_so_far = {}
            for i, field_name in enumerate(all_fields):
                field_decl = typedecl_env.fields[field_name]

                local_vars = {}

                if 'static' in field_decl.modifiers:
                    local_vars = {}

                    static_context_flag = True
                    
                find_and_resolve_names(
                    type_index,
                    cu_env,
                    pkg_name,
                    field_decl.find_child('Initializer'),
                    local_vars,
                    disallowed_simple_names = disallowed
                )

                if static_context_flag:
                    static_context_flag = False

                fields_so_far[field_name] = field_decl
                disallowed.remove(field_name)

def name_link_block(type_index, cu_env, pkg_name, stmts, local_vars):
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

                find_and_resolve_names(type_index, cu_env, pkg_name, stmt[0],
                    local_vars,
                    {var_name:for_vars[0]})

                local_vars[var_name] = for_vars[0]

            find_and_resolve_names(type_index, cu_env, pkg_name, stmt[0],
                local_vars)
            find_and_resolve_names(type_index, cu_env, pkg_name, stmt[1],
                local_vars)
            find_and_resolve_names(type_index, cu_env, pkg_name, stmt[2],
                local_vars)
            
            name_link_block(type_index, cu_env, pkg_name, stmt[3],
                local_vars)

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
                name_link_block(type_index, cu_env, pkg_name, stmt[2],
                    local_vars)
            continue

        if stmt == Node('LocalVariableDeclaration'):
            var_name = list(stmt.select(['LocalVariableDeclaration', 'Identifier']))
            var_name = var_name[0].value.value

            find_and_resolve_names(type_index, cu_env, pkg_name, stmt[2],
                local_vars)

            local_vars[var_name] = stmt

        # find name references
        find_and_resolve_names(type_index, cu_env, pkg_name, stmt, local_vars)

def find_and_resolve_names(type_index, cu_env, pkg_name, stmt, local_vars,
        disallowed_simple_names=None):

    for node in find_nodes(stmt, [Node('Name'), Node('MethodInvocation'),
            Node('FieldAccess'),
            Node('ArrayAccess'),
            Node('Assignment')]):

        if node == Node('MethodInvocation'):
            # node.children = ['MethodName', 'MethodReceiver', 'Arguments']

            # resolve the receiver as much as possible
            meth_recv = node[1]
            if len(meth_recv.children) > 0:
                if meth_recv[0] == Node('Name'):
                    meth_recv_name = '.'.join(meth_recv.leaf_values())
                    name_node = meth_recv[0]
                    resolved_node = name_link_name(type_index, cu_env,
                        pkg_name, local_vars,
                        meth_recv_name.split('.'),
                        disallowed_simple_names)

                    canon_type = resolve_type_by_name(type_index,
                        cu_env,
                        pkg_name,
                        meth_recv_name)
                    
                    # it could an ambig name
                    if resolved_node != None:
                        name_node.decl = resolved_node
                        name_node.typ = resolved_node.find_child('Type').canon
                        name_node.canon = node.typ

                    # it could be a static type
                    elif canon_type != None:
                        name_node.canon = canon_type
                    else:
                        logging.error('method receiver %s could not be resolved!' %
                            (meth_recv_name))
                        sys.exit(42)

                else:
                    # resolve some more!
                    find_and_resolve_names(type_index, cu_env, pkg_name,
                        meth_recv,
                        local_vars,
                        disallowed_simple_names)
                
            # if it has arguments, name resolve those
            if len(node.children) == 3:
                find_and_resolve_names(type_index, cu_env, pkg_name, node[2],
                    local_vars,
                    disallowed_simple_names)
            continue

        elif node == Node('ArrayAccess'):
            # node.children = ['ArrayReceiver', 'Primary']
            find_and_resolve_names(type_index, cu_env, pkg_name, node[0],
                local_vars,
                {})

            find_and_resolve_names(type_index, cu_env, pkg_name, node[1],
                local_vars,
                disallowed_simple_names)

            continue

        elif node == Node('FieldAccess'):
            # this?
            # node.children = ['FieldName', 'FieldReceiver']
            if node[1][0] == Node('This'):
                name = ['this'] + node[0].leaf_values()
            else:
                find_and_resolve_names(type_index, cu_env, pkg_name,
                    node[1],
                    local_vars,
                    disallowed_simple_names)

                continue

        elif node == Node('Assignment'):

            find_and_resolve_names(type_index, cu_env, pkg_name,
                ASTNode(children=[node[0]]),
                local_vars)

            find_and_resolve_names(type_index, cu_env, pkg_name,
                ASTNode(children=[node[1]]),
                local_vars,
                disallowed_simple_names)

            continue

        elif node == Node('Name'):
            name = node.leaf_values()

        resolved_node = name_link_name(type_index, cu_env, pkg_name,
            local_vars,
            name,
            disallowed_simple_names)

        if resolved_node == None:
            logging.error('Could not resolve name %s in %s.%s with %s' % (name, pkg_name,
                cu_env['ClassDeclaration'], local_vars))
            sys.exit(42)

        node.decl = resolved_node
        node.typ = resolved_node.find_child('Type').canon
        #print('resolved %s in %s' % (name, environment.env_type_name(cu_env)))

def member_accessable(class_index, type_index, canon_type, member,
        viewer_canon_type, check_instance=False):

    """
        return ASTNode of member if canon_type.member is accessible from
        viewer_canon_type
    """
    global static_context_flag

    # if second part is in contain set of the first(canon_type), and is not protected, RECURSE
    contain_set = utils.class_hierarchy.contain(class_index[canon_type])
    member_i = -1
    try:
        member_i = contain_set.index(member)
    except ValueError:
        pass

    if member_i >= 0:

        r = contain_set[member_i]
        declaring_canon_type = r.declared_in.name
        
        # you can see it if you're in the same package
        if pkg(viewer_canon_type) == pkg(canon_type):
            return r.node
        # if it's not protected, you can see it
        if 'Protected' not in r.mods:
            return r.node
        else:
            # it's protected? you can see if it its a subclass:

            """
                C is class where member is declared
                - access permitted only in subclass S

                i.e., viewer_canon must be subclass of C
                - asdf.Member, then asdf is subclass of S

                J2_6_ProtectedAccess_StaticField_Super:
                - OK: current type C is a subclass of the declaring type A.A


                J2_6_ProtectedAccess_StaticField_Sub:
                - OK: current type C is a subclass of the declaring type A.A
            """
            
            # member is a constructor
            if isinstance(member, utils.class_hierarchy.Method) and member.type == None:
               return None 

            if is_nonstrict_subclass(declaring_canon_type, viewer_canon_type,
                class_index) == False:
                return None
            
            if check_instance and \
                is_nonstrict_subclass(viewer_canon_type, canon_type,
                    class_index) == False:
                    return None

            return r.node


    return None

def field_accessable(class_index, type_index, canon_type, field_name,
        viewer_canon_type, check_instance=False):
   
    return member_accessable(class_index,
        type_index,
        canon_type,
        Temp_Field(field_name),
        viewer_canon_type,
        check_instance)

def method_accessable(class_index, type_index, canon_type, method_name, params,
        viewer_canon_type, check_instance=False):
    
    return member_accessable(class_index,
            type_index,
            canon_type,
            Temp_Method(method_name, params),
            viewer_canon_type,
            check_instance)

def constructor_accessable(class_index, type_index, canon_type, method_name, params,
        viewer_canon_type, check_instance=False):
    
    return member_accessable(class_index,
            type_index,
            canon_type,
            Temp_Constructor(method_name, params),
            viewer_canon_type,
            check_instance)

def name_link_name(type_index, cu_env, pkg_name, local_vars, name_parts,
        disallowed_simple_names=None,

        check_locals=True,
        check_contains=True,
        check_type=True,
        check_this=True):

    """
        name_parts is an array:
            e.g. ['a', 'b', 'c'] or ['this', 'c'] representing a.b.c or this.c
    """
    global static_context_flag

    name_fields = []
    if len(name_parts) > 0:
        name_fields = name_parts[1:]

    # the contain set of this class
    cu_canon = '%s.%s' % (pkg_name, environment.env_type_name(cu_env))
    cu_contain_set = utils.class_hierarchy.contain(class_index[cu_canon])
    try:
        field_i = cu_contain_set.index(Temp_Field(name_parts[0]))
    except ValueError:
        field_i = -1

    # simple names should be enforced if they exist
    if disallowed_simple_names != None:

        if len(name_parts) == 1 and name_parts[0] in disallowed_simple_names:
            logging.error('Illegal forward declaration reference to %s', name_parts[0])
            sys.exit(42)
            return None

        # special case for array.length
        if len(name_parts) == 2 \
                and name_parts[0] in disallowed_simple_names \
                and field_i != -1 \
                and cu_contain_set[field_i].node.find_child('Type').canon.endswith('[]') \
                and name_parts[1] == 'length':
                logging.error('Illegal forward declaration reference to %s', name_parts[0])
                sys.exit(42)
                return None
 
    candidate = None
    canon_type = None
    is_type = False

    if name_parts[0] == 'this' and check_this:
        return name_link_name(type_index, cu_env, pkg_name,
                local_vars, name_fields)

    # is it a local variable?
    if name_parts[0] in local_vars and check_locals:
        candidate = local_vars[name_parts[0]]
    
    # is it in the contains set?
    elif field_i >= 0 and check_contains:
        candidate = cu_contain_set[field_i].node

        # can't be static in a static context
        if static_context_flag or 'static' in candidate.modifiers:
            logging.error('Cant reference to non-static in a static context')
            return None

    elif check_type:
        # we check the ambiguous name, one part at a time:
        for i, _ in enumerate(name_parts):
            type_candidate = name_parts[:i+1]
            canon_name = resolve_type_by_name(type_index, cu_env, pkg_name,
                                                '.'.join(type_candidate))

            if canon_name:
                if (i+1 != len(name_parts)):
                    canon_type = canon_name
                    name_fields = name_parts[i+1:]
                    is_type = True
                    break

                else:
                    # this is just a type! names can't be types
                    return None
            
    # ACCESS CHECK FOR THE CANDIDATE!
    # first, we get its type if we don't already have it
    if candidate != None and len(name_fields) >= 1:
        # can we access the second part (which is a field) from here?
        
        # get canon type of candidate
        # candidate is a declaration astnode
        canon_type = candidate.find_child('Type').canon

    # now we check if we can access for the field's type
    if canon_type != None and len(name_fields) >= 1:

        # special case of Array
        if canon_type.endswith('[]'):
            if name_fields != ['length']:
                return None
            return primitives.array_length_node

        if primitives.is_primitive(canon_type):
            logging.error('%s is a primitive, does not have field %s' % \
                (name_parts[0], name_fields))
            return None

        fa = field_accessable(class_index, type_index, canon_type,
                name_fields[0], cu_canon, is_type == False)
        if fa != None:

            if is_type:
                if 'static' not in fa.modifiers:
                    # uh oh, this has to be a static field!
                    logging.error('%s is not static of type %s but is being \
                        accessed as one' % (fa, canon_type))
                    return None
            
                static_canon_type = fa.find_child('Type').canon
                
                if len(name_fields) >= 2: # i.e,  MyClass.staticvar.MORESTUFF

                    # switch context static_canon_type and work with the rest of
                    # the name.

                    if static_canon_type.endswith('[]'):

                        if name_fields[1:] == ['length']:
                            return primitives.array_length_node
                        
                        logging.error('Cannot access field %s of static array type %s'
                            % (name_fields[1:], static_canon_type))
                        sys.exit(42)

                    elif primitives.is_primitive(static_canon_type):
                        logging.error('Primitives do not have fields to access!')
                        return None
                        #sys.exit(42)

                    save_static_context = static_context_flag
                    static_context_flag = False

                    fa = name_link_name(type_index,
                            type_index[static_canon_type],
                            name_fields[1:],
                            {}, # no locals
                            check_type=False,
                            check_this=False)
                    
                    static_context_flag = save_static_context
                return fa
            else:
                # not a type -- we can just recurse down
                save_static_context = static_context_flag
                static_context_flag = False

                ret = name_link_name(type_index, type_index[canon_type],
                            canon_type.rsplit('.', 1)[0],
                        {},
                        name_fields,
                        check_type=check_type,
                        check_this=check_this)

                static_context_flag = save_static_context
                return ret
        else:
            return None
    
    return candidate

def pkg(canon_type):
    return canon_type.rsplit('.', 1)[0]
