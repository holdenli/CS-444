
import sys

from utils import logging

from utils.node import Node
from utils.node import find_nodes
import environment

from typelink import resolve_type_by_name

import utils.class_hierarchy 
from utils.class_hierarchy import Temp_Field

class_index = {}

def name_link(pkg_index, type_index, cls_idx):
    global class_index
    class_index = cls_idx

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

    for node in find_nodes(stmt, [Node('Name'), Node('MethodInvocation')]):
        if node == Node('MethodInvocation'):
            # node.children = ['MethodName', 'MethodReceiver', 'Arguments']
            name = node[1].leaf_values() + node[0].leaf_values()

            # if it has arguments, name resolve those
            if len(node.children) == 3:
                find_and_resolve_names(type_index, cu_env, pkg_name, node[2],
                    local_vars)

            # FIXME: now resolve the method name itself
            continue

        elif node == Node('Name'):
            name = node.leaf_values()

        resolved_node = name_link_name(type_index, cu_env, pkg_name, local_vars, '.'.join(name))

        if resolved_node == None:
            logging.error('Could not resolve name %s in %s.%s with %s' % (name, pkg_name,
                cu_env['ClassDeclaration'], local_vars))
            sys.exit(42)
        
        #print('resolved %s in %s' % (name, environment.env_type_name(cu_env)))

def name_link_name(type_index, cu_env, pkg_name, local_vars, name):

    def find_field(typedecl_env, name):
        if name in typedecl_env.fields:
            return typedecl_env.fields[name]

        # lets check the parent class instead
        super_node = typedecl_env.node.find_child('Superclass')
        if super_node.children:
            super_env = list(super_node.select(['ReferenceType']))[0].env
            return find_field(super_env['ClassDeclaration'], name)

        return None

    name_parts = name.split('.')
    
    # is it a local variable?
    if name_parts[0] in local_vars:
        return local_vars[name_parts[0]]

    # is it in the contains set?
    canon_type = '%s.%s' % (pkg_name, environment.env_type_name(cu_env))
    
    fields = utils.class_hierarchy.contain(class_index[canon_type])
    field = Temp_Field(name_parts[0])
    if field in fields:
        # FIXME: should return the Field's node
        return Node()

    # is it a type?
    for i, _ in enumerate(name_parts):
        type_candidate = name_parts[:i+1] 
        canon_name = resolve_type_by_name(type_index, cu_env, pkg_name,
                                            '.'.join(type_candidate))

        if canon_name and (i+1 != len(name_parts)):
            canon_pkg = canon_name.rsplit('.', 1)[0]
            # make sure we can resolve 
            return name_link_name(type_index, type_index[canon_name], canon_pkg,
                {}, '.'.join(name_parts[i+1:]))

            #return environment.env_type_name(type_index[canon_name])

    return None
