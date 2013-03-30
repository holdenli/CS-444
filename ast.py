#!/usr/bin/python3

import sys
from utils import logging
from utils.node import ASTNode
from utils.node import Node

# Processes the provide parse tree (root) node and returns the root ASTNode
# of the abstract syntax tree of the input.
# This is destructive - parse_tree should not be used afterwards.
def build_ast(parse_tree):
    ast = ASTNode('Root')
    
    # Start with CompilationUnit.
    unit = parse_tree.find_child('CompilationUnit')
    if unit is not None:
        cu = ASTNode('CompilationUnit')
        ast.add(build_top_level(ASTNode('CompilationUnit'), unit))

    # Make sure that we use AST nodes.
    # ensure_ast_children(ast)

    return ast

# Given the AST node of a Compilation Unit being constructed, and the
# CompilationUnit node of a parse tree, determine the top-level structure
# of the AST.
def build_top_level(ast, unit):
    # Extract package declaration, if it exists.
    pkg = ASTNode('PackageDeclaration')
    package_decl = unit.find_child('PackageDeclaration')
    if package_decl is not None:
        #pkg.children = flatten_name(package_decl[1])
        pkg = flatten(package_decl[1], 'PackageDeclaration', 'Identifier')
    ast.add(pkg)

    # Extract imports, if they exist.
    typ_imports = ASTNode('TypeImports')
    pkg_imports = ASTNode('PackageImports')
    import_decl = unit.find_child('ImportDeclarations')
    if import_decl is not None:
        typ_imports.children, pkg_imports.children = flatten_imports(import_decl)
    ast.add(typ_imports)
    ast.add(pkg_imports)

    # Extract type declaration.
    typ_decl = unit.find_child('TypeDeclarations')
    if typ_decl is not None and typ_decl[0][0].name != 'SemiColon':
        if typ_decl[0][0].name == 'ClassDeclaration':
            typ = build_class_structure(typ_decl[0][0])
        elif typ_decl[0][0].name == 'InterfaceDeclaration':
            typ = build_interface_structure(typ_decl[0][0])
        ast.add(typ)

    return ast

# Helper for flattening import declarations.
def flatten_imports(node):
    typ_imports = []
    pkg_imports = []

    while node.first.name != 'ImportDeclaration':

        # ImportDeclarations => ImportDeclarations ImportDeclaration
        id_list = flatten(node[1][0][1], 'Name', 'Identifier')

        # Append to appropriate list.
        if node[1][0].name == 'SingleTypeImportDeclaration':
            typ_imports.append(ASTNode('ImportDeclaration', None, id_list.children))
        else:
            pkg_imports.append(ASTNode('ImportDeclaration', None, id_list.children))

        node = node[0]


    # ImportDeclarations => ImportDeclaration
    id_list = flatten(node[0][0][1], 'Name', 'Identifier')

    # Append to appropriate list.
    if node[0][0].name == 'SingleTypeImportDeclaration':
        typ_imports.append(ASTNode('ImportDeclaration', None, id_list.children))
    else:
        pkg_imports.append(ASTNode('ImportDeclaration', None, id_list.children))

    typ_imports.reverse()
    pkg_imports.reverse()
    return (typ_imports, pkg_imports)

# Builds the AST node for a type declaration. Assumes that the node is a
# ClassDeclaration.
def build_class_structure(node):
    decl_node = ASTNode('ClassDeclaration')

    # Add modifiers and name (same for classes and interfaces).
    decl_node.add(flatten_leaves(node[0], 'Modifiers'))
    decl_node.add(ASTNode('ClassName', None, [node[2]]))

    # Extract superclass.
    superstuff = node.find_child('SuperStuff')
    if superstuff is None:
        decl_node.add(ASTNode('Superclass'))
    else:
        typ = ASTNode('Type', None,
            [flatten(superstuff, 'ReferenceType', 'Identifier')])
        decl_node.add(ASTNode('Superclass', None, [typ]))

    # Extract interface implements.
    interfaces = ASTNode('Interfaces')
    decl_ints = node.find_child('Interfaces')
    if decl_ints is not None:
        interfaces = flatten_interfaces(decl_ints)
    decl_node.add(interfaces)

    body = node.find_child('ClassBody')
    if body is None:
        logging.error("AST: missing ClassBody")
        sys.exit(1)

    # Extract fields, constructors, and methods.
    members = flatten(body, 'Members', 'ClassBodyDeclaration')
    fields = flatten(members, 'Fields', 'FieldDeclaration')
    decl_node.add(build_fields(fields))
    constructors = flatten(members, 'Constructors', 'ConstructorDeclaration')
    decl_node.add(build_constructors(constructors))
    methods = flatten(members, 'Methods', 'MethodDeclaration')
    decl_node.add(build_methods(methods))

    return decl_node

# Returns a processed Fields AST node for the input Fields node.
def build_fields(node):
    fields = ASTNode('Fields')
    for field_decl in node.children:
        field = ASTNode('FieldDeclaration')
        if hasattr(field_decl, 'decl_order'):
            field.decl_order = field_decl.decl_order
        else:
            field.decl_order = -1

        # Extract modifiers.
        field.add(flatten_leaves(field_decl[0], 'Modifiers'))

        # Extract type.
        field.add(build_type(field_decl[1]))

        # Extract name.
        field.add(field_decl[2][0][0][0])

        # Extract initializer.
        var_declr = field_decl[2][0] # VariableDeclarator
        if len(var_declr.children) > 1:
            initializer = build_expr(var_declr[2][0])
            field.add(ASTNode('Initializer', None, [initializer]))
        else:
            field.add(ASTNode('Initializer')) # No initializer

        fields.add(field)

    return fields

def build_constructors(node):
    constructors = ASTNode('Constructors')
    for cons_decl in node.children:
        cons = ASTNode('ConstructorDeclaration')
        if hasattr(cons_decl, 'decl_order'):
            cons.decl_order = cons_decl.decl_order
        else:
            cons.decl_order = -1

        # Extract modifiers.
        cons.add(flatten_leaves(cons_decl[0], 'Modifiers'))

        # Extract name.
        cons.add(cons_decl[1][0][0]) # Name

        # Extract parameters.
        if cons_decl[1][2].name == 'FormalParameterList':
            cons.add(build_parameters(cons_decl[1][2]))
        else:
            cons.add(ASTNode('Parameters'))

        # Extract body.
        cons.add(build_block(cons_decl[2]))

        constructors.add(cons)

    return constructors

def build_methods(node):
    methods = ASTNode('Methods')
    for method_decl in node.children:
        method = ASTNode('MethodDeclaration')
        if hasattr(method_decl, 'decl_order'):
            method.decl_order = method_decl.decl_order
        else:
            method.decl_order = -1

        # Extract modifiers.
        method.add(flatten_leaves(method_decl[0][0], 'Modifiers'))

        # Extract return type.
        if method_decl[0][1].name == 'Void':
            method.add(ASTNode('Type', None, [method_decl[0][1]]))
        else:
            method.add(build_type(method_decl[0][1])) # Non-void.

        # Name.
        method.add(method_decl[0][2][0])
 
        # Extract parameters.
        if method_decl[0][2][2].name == 'FormalParameterList':
            method.add(build_parameters(method_decl[0][2][2]))
        else:
            method.add(ASTNode('Parameters'))

        # Extract body.
        # We have two levels, for differentiating between:
        # 1. Methods with no body (i.e., abstract)
        # 2. Methods with an empty body (i.e., {})
        # 3. Methods with a nonempty body
        body = ASTNode('MethodBody')
        if method_decl[1].name != 'SemiColon' and \
                method_decl[1][0].name != 'SemiColon':
            body.add(build_block(method_decl[1][0]))
        method.add(body)

        methods.add(method)

    return methods        

# Returns a processed Type node.
def build_type(node):
    typ = ASTNode('Type')
    # return node
    if node[0].name == 'PrimitiveType':
        typ.add(flatten_leaves(node[0], 'PrimitiveType'))
    elif node[0][0].name == 'ClassOrInterfaceType':
        typ.add(flatten(node[0][0], 'ReferenceType', 'Identifier'))
    elif node[0][0][0].name == 'PrimitiveType': # ArrayType of PrimitiveType
        typ.add(ASTNode('ArrayType', None,
            [flatten_leaves(node[0][0][0], 'PrimitiveType')]))
    else: # ArrayType of ClassOrInterfaceType
        typ.add(ASTNode('ArrayType', None,
            [flatten(node[0][0][0], 'ReferenceType', 'Identifier')]))

    return typ

# Returns a processed Parameters node, given a FormalParameterList node of the
# parse tree.
def build_parameters(node):
    params = ASTNode('Parameters')

    # Get a list of FormalParameter.
    param_decls = flatten(node, 'Parameters', 'FormalParameter')
    for param_decl in param_decls.children:
        param = ASTNode('Parameter')
        param.add(build_type(param_decl[0]))
        param.add(param_decl[1][0]) # Name

        params.add(param)

    return params

# Builds the AST node for an interface declaration. node must be an
# InterfaceDeclaration.
def build_interface_structure(node):
    decl_node = ASTNode('InterfaceDeclaration')

    # Add modifiers and name (same for classes and interfaces).
    decl_node.add(flatten_leaves(node[0], 'Modifiers'))
    decl_node.add(ASTNode('InterfaceName', None, [node[2]]))

    # Extract interface extends.
    interfaces = ASTNode('Interfaces')
    decl_ints = node.find_child('ExtendsInterfaces')
    if decl_ints is not None:
        interfaces = flatten_interfaces(decl_ints)
    decl_node.add(interfaces)

    body = node.find_child('InterfaceBody')
    if body is None:
        logging.error("AST: missing InterfaceBody")
        sys.exit(1)

    # Joos only allows methods to be in interfaces.
    methods = flatten(body, 'Methods', 'InterfaceMemberDeclaration')
    decl_node.add(build_methods(methods)) 

    return decl_node

def build_block(node):
    block = ASTNode('Block')

    # If no statements, return empty block.
    if node[1].name != 'BlockStatements':
        return block

    blk_stmts = flatten(node[1], 'Statements', 'BlockStatement')

    for blk_stmt in blk_stmts.children:

        # Local variable declaration.
        if blk_stmt[0].name == 'LocalVariableDeclarationStatement':
            block.add(build_local_variable_declaration(blk_stmt[0][0]))

        else: # Statement
            block.add(build_statement(blk_stmt[0]))

    return block

# Builds the AST node for a LocalVariableDeclaration.
def build_local_variable_declaration(node):
    local_var = ASTNode('LocalVariableDeclaration')
    local_var.add(build_type(node[0]))

    # Extract name and initializer.
    var_declr = node[1][0]
    local_var.add(var_declr[0][0])
    if len(var_declr.children) > 1:
        initializer = build_expr(var_declr[2][0])
        local_var.add(ASTNode('Initializer', None, [initializer]))
    else:
        local_var.add(ASTNode('Initializer')) # No initializer

    return local_var


# Builds the AST node for an input Statement or StatementNoShortIf node.
# Statements with a "NoShortIf" are executed with the same semantics as
# statements without the "NoShortIf", as per JLS section 14.4.
def build_statement(node):
    if_statements = [
        'IfThenStatement',
        'IfThenElseStatement',
        'IfThenElseStatementNoShortIf',
    ]

    if node[0].name == 'StatementWithoutTrailingSubstatement':
        return build_statement_wts(node[0])
    elif node[0].name in if_statements:
        return build_if_statement(node[0])
    elif node[0].name in ['WhileStatement', 'WhileStatementNoShortIf']:
        return build_while_statement(node[0])
    elif node[0].name in ['ForStatement', 'ForStatementNoShortIf']:
        return build_for_statement(node[0])
    else:
        logging.error('AST: invalid node in build_statement()')
        sys.exit(1)

# Builds the AST node for a StatementWithoutTrailingSubstatement node.
def build_statement_wts(node):
    if node[0].name == 'Block':
        return build_block(node[0])

    elif node[0].name == 'EmptyStatement':
        return ASTNode('EmptyStatement')

    # ExpressionStatement => StatementExpression.
    elif node[0].name == 'ExpressionStatement':
        expr_stmt = ASTNode('ExpressionStatement')
        expr_stmt.add(build_expr(node[0][0]))
        return expr_stmt

    else: # ReturnStatement
        return_stmt = ASTNode('ReturnStatement')
        if node[0][1].name == 'Expression':
            return_stmt.add(build_expr(node[0][1]))
        return return_stmt

# Builds the AST node for Expression, StatementExpression, and their recursive
# expression types.
def build_expr(node):
    skipped_expressions = [
        'ConditionalExpression',
        'ShiftExpression',
        'ExclusiveOrExpression',
    ]
    binary_expressions = [
        'ConditionalOrExpression',
        'ConditionalAndExpression',
        'EqualityExpression',
        'AndExpression',
        'InclusiveOrExpression',
        # 'RelationalExpression', # have to check special case Instanceof
        'AdditiveExpression',
        'MultiplicativeExpression',
    ]

    if node.name == 'StatementExpression':
        if node[0].name == 'Assignment':
            return build_assignment(node[0])
        elif node[0].name == 'MethodInvocation':
            return build_method_invocation(node[0])
        elif node[0].name == 'ClassInstanceCreationExpression':
            return build_creation_expression(node[0])

    elif node.name == 'Expression':
        return build_expr(node[0]) # Recurse on AssignmentExpression

    elif node.name == 'AssignmentExpression':
        if node[0].name == 'Assignment':
            return build_assignment(node[0])
        else:
            return build_expr(node[0])

    elif node.name in skipped_expressions:
        return build_expr(node[0])

    elif node.name in binary_expressions:
        if len(node.children) == 1: # recurse
            return build_expr(node[0])
        else:
            return build_binary_expression(node)

    elif node.name == 'RelationalExpression':
        if len(node.children) == 1: # recurse
            return build_expr(node[0])
        elif node[1].name == 'Instanceof':
            return build_instanceof_expression(node)
        else:
            return build_binary_expression(node)

    elif node.name in ['UnaryExpression', 'UnaryExpressionNotPlusMinus']:
        if len(node.children) == 1:
            return build_expr(node[0])
        elif node[0].name == 'SubtractOperator':
            return ASTNode('NegateExpression', None, [build_expr(node[1])])
        elif node[0].name == 'NotOperator':
            return ASTNode('NotExpression', None, [build_expr(node[1])])

    elif node.name == 'PostfixExpression':
        if node[0].name == 'Primary':
            return ASTNode('PostfixExpression', None, [build_primary(node[0])])
        else: # Name
            return ASTNode('PostfixExpression', None,
                [flatten(node[0], 'Name', 'Identifier')])

    elif node.name == 'CastExpression':
        return build_cast_expression(node)

    else: # Should not happen.
        logging.error("AST: Unknown expression")
        sys.exit(1) # Crash

def build_cast_expression(node):
    cast_expr = ASTNode('CastExpression')
    typ = ASTNode('Type')
    if node[2].name == 'Dims': # array type
        if node[1].name == 'PrimitiveType':
            typ.add(ASTNode('ArrayType', None,
                [flatten_leaves(node[1], 'PrimitiveType')]))
        else: # Name
            typ.add(ASTNode('ArrayType', None,
                [flatten(node[1], 'ReferenceType', 'Identifier')]))

    elif node[1].name == 'Expression': # Actually a name.
        typ.add(flatten(node[1], 'ReferenceType', 'Identifier'))
    else: # PrimitiveType
        typ.add(flatten_leaves(node[1], 'PrimitiveType'))

    cast_expr.add(typ)

    # Last child is the thing we're casting.
    cast_expr.add(build_expr(node[-1]))

    return cast_expr

# Builds the AST node for ClassInstanceCreationExpression and
# ArrayCreationExpression.
# TODO: Decide whether to split these.
def build_creation_expression(node):
    creation = ASTNode('CreationExpression')

    # We do some funky stuff to make sure that it matches 'Type'.
    typ = ASTNode('Type')

    # Note: both creation expression types have ClassType at second index.
    # For ArrayCreationExpression, we actually need to nest the type.
    if node.name == 'ArrayCreationExpression':
        # Type => ArrayType => PrimitiveType
        if node[1].name == 'PrimitiveType':
            typ.add(ASTNode('ArrayType', None,
                [flatten_leaves(node[1], 'PrimitiveType')]))
        # Type => ArrayType => ReferenceType
        else:
            typ.add(ASTNode('ArrayType', None,
                [flatten(node[1], 'ReferenceType', 'Identifier')]))

    else: # ClassInstanceCreationExpression
        if node[1].name == 'PrimitiveType':
            typ.add(flatten_leaves(node[1], 'PrimitiveType'))
        else:
            typ.add(flatten(node[1], 'ReferenceType', 'Identifier'))

    creation.add(typ)

    # Get the arguments.
    args = ASTNode('Arguments')
    if node.name == 'ArrayCreationExpression':
        if node[2].name == 'DimExprs':
            args.add(build_expr(node[2][0][1]))
    else: # ClassInstanceCreationExpression
        if node[3].name == 'ArgumentList':
            args = build_arguments(node[3])
    
    creation.add(args)
    
    return creation

def build_instanceof_expression(node):
    expr = build_expr(node[0]) # Left hand side.

    # Hack in a type node for use with build_type().
    typ = build_type(ASTNode('Type', None, [node[2]]))

    return ASTNode('InstanceofExpression', None, [expr, typ])

# Builds an expression node, given an input node of the form
# [expression, operator, expression].
def build_binary_expression(node):
    if len(node.children) != 3:
        logging.error('FATAL ERROR: build_binary_expression()')
        sys.exit(1)

    valid_operators = {
        'EqualOperator',
        'NotEqualOperator',
        'AndOperator',
        'OrOperator',
        'LessThanOperator',
        'LessThanEqualOperator',
        'GreaterThanOperator',
        'GreaterThanEqualOperator',
        'BinaryAndOperator',
        'BinaryOrOperator',
        'AddOperator',
        'SubtractOperator',
        'MultiplyOperator',
        'DivideOperator',
        'ModuloOperator',
    }

    lhs = build_expr(node[0])
    rhs = build_expr(node[2])

    # Check that the operator is valid, and convert it to a corresponding
    # expression node (done by stripping "Operator" and replacing it with
    # "Expression").
    if node[1].name in valid_operators:
        node_name = node[1].name[:-len('Operator')] + 'Expression'
        return ASTNode(node_name, None, [lhs, rhs])
    else:
        logging.error('FATAL ERROR: Invalid operator %s encountered in build_binary_expression()' % node[1].name)
        sys.exit(1)

def build_method_invocation(node):
    method_invo = ASTNode('MethodInvocation')

    # First, extract the method name and receiver (i.e., the "thing we're
    # calling the method on").
    method_receiver = ASTNode('MethodReceiver')
    if node[0].name == 'Name':
        qualified_name = flatten(node[0], 'MethodName', 'Identifier')
        
        # If the name is qualified (i.e., more than 1 Identifier), we take the
        # last Identifier to be the method name. There is a method receiver
        # only if there are at least 2 identifiers.
        # Note that the latter case of no method receivers declared is possible
        # since Joos allows "implicit this for methods".
        if len(qualified_name.children) == 1:
            method_invo.add(qualified_name)
        else:
            method_name = qualified_name.children.pop()
            method_invo.add(ASTNode('MethodName', None, [method_name]))
            qualified_name.name = 'Name'
            method_receiver.add(qualified_name)

    else: # Name is at position 2, receiver is the Primary at position 0.
        method_invo.add(ASTNode('MethodName', None, [node[2]]))
        method_receiver.add(build_primary(node[0]))

    method_invo.add(method_receiver)
            
    method_args = node.find_child('ArgumentList')
    if method_args is not None:
        method_invo.add(build_arguments(method_args))
    else:
        method_invo.add(ASTNode('Arguments'))

    return method_invo

def build_arguments(node):
    arguments = ASTNode('Arguments')
    args = flatten(node, 'Arguments', 'Expression')
    for arg in args:
        arguments.add(build_expr(arg))
    return arguments

# Builds the AST node given a Primary expression (i.e., the simplest form of an
# expression). It's highly recommended to read JLS 15.7 before trying to
# understand this code.
# Also handles PrimaryNoNewArray.
def build_primary(node):
    if node.name == 'Primary':
        if node[0].name == 'ArrayCreationExpression':
            return build_creation_expression(node[0])
        else:
            return build_primary(node[0]) # Recurse on PrimaryNoNewArray.
    # Otherwise, it's a PrimaryNoNewArray.
    elif node[0].name in ['Literal', 'This']:
        return node[0]
    elif len(node.children) > 1: # Parenthesized expression.
        return build_expr(node[1])
    elif node[0].name == 'ClassInstanceCreationExpression':
        return build_creation_expression(node[0])
    elif node[0].name == 'FieldAccess':
        return build_field_access(node[0])
    elif node[0].name == 'MethodInvocation':
        return build_method_invocation(node[0])
    elif node[0].name == 'ArrayAccess':
        return build_array_access(node[0])
    else:
        logging.error('AST: Invalid Primary in build_primary()')
        sys.exit(1)

def build_field_access(node):
    field_access = ASTNode('FieldAccess')
    field_access.add(ASTNode('FieldName', None, [node[2]]))
    if node[0].name == 'Primary':
        field_access.add(ASTNode('FieldReceiver', None, [build_primary(node[0])]))
    else: # Super
        field_access.add(ASTNode('FieldReceiver', None, [node[0]]))
    return field_access

def build_assignment(node):
    assignment = ASTNode('Assignment')
    assignment.add(build_left_hand_side(node[0]))
    assignment.add(build_expr(node[2]))
    return assignment

def build_left_hand_side(node):
    if node[0].name == 'Name':
        return flatten(node[0], 'Name', 'Identifier')
    elif node[0].name == 'FieldAccess':
        return build_field_access(node[0])
    else:
        return build_array_access(node[0])

def build_array_access(node):
    array_access = ASTNode('ArrayAccess')

    # Determine the receiver (i.e., array being accessed).
    array_receiver = ASTNode('ArrayReceiver')
    if node[0].name == 'Name':
        array_receiver.add(flatten(node[0], 'Name', 'Identifier'))
    else:
        array_receiver.add(build_primary(node[0]))
    array_access.add(array_receiver)
    
    # Get the accessing expression.
    array_access.add(build_expr(node[2]))

    return array_access

def build_if_statement(node):
    stmt = ASTNode('IfStatement')
    stmt.add(build_expr(node[2])) # Condition
    stmt.add(build_statement(node[4]))

    if len(node.children) > 5: # Else
        stmt.add(build_statement(node[6]))

    return stmt

def build_while_statement(node):
    stmt = ASTNode('WhileStatement')
    stmt.add(build_expr(node[2])) # Condition
    stmt.add(build_statement(node[4]))
    return stmt

def build_for_statement(node):
    stmt = ASTNode('ForStatement')
    for_init = node.find_child('ForInit')
    for_cond = node.find_child('Expression')
    for_updt = node.find_child('ForUpdate')
    for_body = node.find_child('StatementNoShortIf')
    if for_body is None:
        for_body = node.find_child('Statement')

    init_node = ASTNode('ForInit')
    if for_init is not None:
        if for_init[0].name == 'StatementExpressionList':
            init_node.add(build_expr(for_init[0][0]))
        else: # LocalVariableDeclaration
            init_node.add(build_local_variable_declaration(for_init[0]))
    stmt.add(init_node)

    cond_node = ASTNode('ForCondition')
    if for_cond is not None:
        cond_node.add(build_expr(for_cond))
    stmt.add(cond_node)

    updt_node = ASTNode('ForUpdate')
    if for_updt is not None:
        updt_node.add(build_expr(for_updt[0][0]))
    stmt.add(updt_node)

    body_node = ASTNode('ForBody')
    if for_body is not None:
        body_node.add(build_statement(for_body))
    stmt.add(body_node)

    return stmt

def flatten_interfaces(node):
    interfaces = ASTNode('Interfaces')

    # Find all InterfaceType nodes.
    int_types = flatten(node, 'Interfaces', 'InterfaceType')

    # Flatten each InterfaceType name.
    for int_type in int_types.children:
        typ = ASTNode('Type', None,
            [flatten(int_type, 'ReferenceType', 'Identifier')])
        interfaces.add(typ)

    return interfaces

# Given a node, find all occurrences of leaf_name and returns a node with
# root_name with all occurrences of leaf_name in node as its children.
# Children are in-order.
def flatten(node, root_name, leaf_name):
    root = ASTNode(root_name)
    stack = [node]

    while len(stack) > 0:
        n = stack.pop()
        if n.name == leaf_name:
            root.add(n)
        else:
            stack.extend(n.children)

    root.children.reverse()

    return root

# Given a node, find all the leaves in-order, and returns them as children of
# a node node with name root_name.
def flatten_leaves(node, root_name):
    root = ASTNode(root_name)
    stack = node.children
    
    while len(stack) > 0:
        n = stack.pop()
        if len(n.children) == 0:
            root.add(n)
        else:
            stack.extend(n.children)

    root.children.reverse()

    return root

# Makes a simple root_name => identifiers structure.
def make_name_node(root_name, identifiers):
    return ASTNode(root_name, None,
        [ASTNode('Identifier', id) for identifier in identifiers])

# Recursively converts all nodes to ASTNodes.
def ensure_ast_children(node):
    for i in range(0, len(node.children)):
        if node[i].__class__ == Node:
            node.children[i] = ASTNode(node[i].name, node[i].value, node[i].children)
        ensure_ast_children(node[i])
            # logging.error(node[i].value)

###############################################################################

# Convenience functions

# Returns a string of the qualified name of a node
# This assume it has a list of identifiers as children
def get_qualified_name(node):
    s = ""
    if node == None:
        return ""
    for i in node.children:
        s += "." + i.value.value
    return s[1:]

def get_modifiers(node):
    if node == None:
        return []
    m = []
    for i in node.children:
        m.append(i.name)
    return m

