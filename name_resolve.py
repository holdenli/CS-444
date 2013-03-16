
import sys

from utils import logging

from utils.node import Node
from utils.node import find_nodes
import environment

from typelink import resolve_type_by_name

import utils.class_hierarchy 
from utils.class_hierarchy import Temp_Field, Temp_Method

class_index = {}

def name_link(pkg_index, type_index, cls_idx):
    global class_index
    class_index = cls_idx

    for pkg_name in pkg_index:
        for cu_env in pkg_index[pkg_name]:
            if cu_env['ClassDeclaration'] == None:
                continue

            typedecl_env = cu_env['ClassDeclaration']

            # name link everything inside methods!
            for method_env in typedecl_env.children:
                method_node = method_env.node
                for block_node in method_node.select(['Block']):
                    name_link_block(type_index, cu_env, pkg_name, block_node,
                            local_vars=environment.build_method_params(method_node))

                    if len(list(method_node.select(['This']))) > 0 \
                        and 'static' in method_node.modifiers:

                        logging.error("Cannot use 'this' inside static method")
                        sys.exit(42)

            # name link field initializers
            field_names = {}
            for field_decl in typedecl_env.node.select(['Fields',
                'FieldDeclaration']):

                field_name = field_decl.find_child('Identifier').value.value
                find_and_resolve_names(
                    type_index,
                    cu_env,
                    pkg_name,
                    field_decl.find_child('Initializer'),

                    local_vars=field_names,
                    lhs_only_vars={field_name:field_decl},
                    check_fields=False
                )
                
                field_names[field_name] = field_decl

def name_link_block(type_index, cu_env, pkg_name, stmts,
        local_vars):

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
                name_link_block(type_index, cu_env, pkg_name, block_stmt,
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
                local_vars,
                lhs_only_vars={var_name:stmt})

            local_vars[var_name] = stmt

        # find name references
        find_and_resolve_names(type_index, cu_env, pkg_name, stmt, local_vars)

def find_and_resolve_names(type_index, cu_env, pkg_name, stmt, local_vars,
        lhs_only_vars=None,
        check_fields=True):

    if lhs_only_vars == None:
        lhs_only_vars = {}

    for node in find_nodes(stmt, [Node('Name'), Node('MethodInvocation'),
            Node('FieldAccess'),
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
                        check_fields)

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
                        print(local_vars)
                        logging.error('method receiver %s could not be resolved!' %
                            (meth_recv_name))
                        sys.exit(42)

                else:
                    # resolve some more!
                    find_and_resolve_names(type_index, cu_env, pkg_name,
                        meth_recv,
                        local_vars,
                        lhs_only_vars,
                        check_fields)
                
            # if it has arguments, name resolve those
            if len(node.children) == 3:
                find_and_resolve_names(type_index, cu_env, pkg_name, node[2],
                    local_vars,
                    lhs_only_vars,
                    check_fields)

            continue

        elif node == Node('FieldAccess'):
            # this?
            # node.children = ['FieldName', 'FieldReceiver']
            if node[1][0] == Node('This'):
                name = node[0].leaf_values()
                check_fields = False
            else:
                continue

        elif node == Node('Assignment'):
            new_vars = dict(local_vars)
            new_vars.update(lhs_only_vars)

            find_and_resolve_names(type_index, cu_env, pkg_name, node[0],
                new_vars,
                {},
                check_fields)

            find_and_resolve_names(type_index, cu_env, pkg_name, node[1],
                local_vars,
                lhs_only_vars,
                check_fields)

            continue

        elif node == Node('Name'):
            name = node.leaf_values()

        resolved_node = name_link_name(type_index, cu_env, pkg_name, local_vars,
            name, check_fields)
        
        if resolved_node == None:
            logging.error('Could not resolve name %s in %s.%s with %s' % (name, pkg_name,
                cu_env['ClassDeclaration'], local_vars))
            sys.exit(42)

        node.decl = resolved_node
        node.typ = resolved_node.find_child('Type').canon
        #print('resolved %s in %s' % (name, environment.env_type_name(cu_env)))

def member_accessable(class_index, type_index, canon_type, member, viewer_canon_type):
        """
            return ASTNode of field if canon_type.field is accessible from
            viewer_canon_type
        """
        
        # if second part is in contain set of the first(canon_type), and is not protected, RECURSE
        contain_set = utils.class_hierarchy.contain(class_index[canon_type])
        field_i = -1
        try:
            field_i = contain_set.index(member)
        except ValueError:
            pass

        if field_i >= 0 and (pkg(viewer_canon_type) == pkg(canon_type) or \
            'protected' not in contain_set[field_i].node.modifiers):
                # name was 'a.b.c.d'
                # we now try to link 'b.c.d' in the context of 'a'
                return contain_set[field_i].node
        else:
            return None

def field_accessable(class_index, type_index, canon_type, field_name, viewer_canon_type):
   
    return member_accessable(class_index,
        type_index,
        canon_type,
        Temp_Field(field_name),
        viewer_canon_type)

def method_accessable(class_index, type_index, canon_type, method_name, params, viewer_canon_type):
    
    return member_accessable(class_index,
            type_index,
            canon_type,
            Temp_Method(method_name, params),
            viewer_canon_type)

def name_link_name(type_index, cu_env, pkg_name, local_vars, name_parts,
                    check_fields=True):
    """
        name_parts is an array:
            e.g. ['a', 'b', 'c'] or ['this', 'c'] representing a.b.c or this.c
    """
 
    candidate = None

    name_fields = []
    if len(name_parts) > 0:
        name_fields = name_parts[1:]
    
    cu_canon = '%s.%s' % (pkg_name, environment.env_type_name(cu_env))
    cu_contain_set = utils.class_hierarchy.contain(class_index[cu_canon])
    try:
        field_i = cu_contain_set.index(Temp_Field(name_parts[0]))
    except ValueError:
        field_i = -1

    canon_type = None

    # is it a local variable?
    if name_parts[0] in local_vars:
        candidate = local_vars[name_parts[0]]
    
    # is it in the contains set?
    elif field_i >= 0 and check_fields:
        candidate = cu_contain_set[field_i].node

    else:
        # is it a type?
        for i, _ in enumerate(name_parts):
            type_candidate = name_parts[:i+1]
            canon_name = resolve_type_by_name(type_index, cu_env, pkg_name,
                                                '.'.join(type_candidate))

            if canon_name:
                if (i+1 != len(name_parts)):
                    canon_type = canon_name
                    name_fields = name_parts[i+1:]
                else:
                    # this is just a type! names can't be types
                    return None
            
    # ACCESS CHECK FOR THE CANDIDATE!
    # first, we get its type if we don't already have it
    if candidate != None and len(name_fields) > 0:
        # can we access the second part (which is a field) from here?
        
        # get canon type of candidate
        # candidate is a declaration astnode
        canon_type = candidate.find_child('Type').canon

    # now we check if we can access for the field's type
    if canon_type != None and len(name_fields) > 0:

        # special case of Array
        if canon_type.endswith('[]'):
            if name_fields != ['length']:
                return None
            return candidate

        if field_accessable(class_index, type_index, canon_type, name_fields[0], cu_canon) != None:
            return name_link_name(type_index, type_index[canon_type],
                canon_type.rsplit('.', 1)[0],
                {},
                name_fields,
                check_fields)
        else:
            return None
    
    return candidate

def pkg(canon_type):
    return canon_type.rsplit('.', 1)[0]
