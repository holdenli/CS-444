import sys
from utils import node

def typecheck(type_index, class_index):
    for type_name, env in type_index.items():
        c = class_index[type_name]
        typecheck_methods(c, env, type_index)

def typecheck_methods(c, env, type_index):
    if c.interface:
        return
    for method_env in env['ClassDeclaration'].children:
        n = method_env.node
        exprs = []
        exprs.extend(n.select(['Assignment']))
        exprs.extend(n.select(['MethodInvocation']))
        exprs.extend(n.select(['CreationExpression']))
        exprs.extend(n.select(['ConditionalOrExpression']))
        exprs.extend(n.select(['ConditionalAndExpression']))
        exprs.extend(n.select(['InclusiveOrExpression']))
        exprs.extend(n.select(['ExclusiveOrExpression']))
        exprs.extend(n.select(['AndExpression']))
        exprs.extend(n.select(['EqualityExpression']))
        exprs.extend(n.select(['AdditiveExpression']))
        exprs.extend(n.select(['MultiplicativeExpression']))
        exprs.extend(n.select(['RelationalExpression']))
        exprs.extend(n.select(['InstanceofExpression']))
        exprs.extend(n.select(['UnaryExpression']))
        exprs.extend(n.select(['PostfixExpression']))
        exprs.extend(n.select(['CastExpression']))
        for expr in exprs:
            typecheck_expr(expr, c, env, type_index)
#
# Type check functions.
# Each type check function must do the following:
# 1. Determine the correct type of the input node.
# 2. Assign the above type to the input node.
# 3. Return the assigned type, so that it can be used by the caller.

def typecheck_expr(node, c, class_env, type_index):
    pass

def typecheck_literal(class_env, local_env, return_type, node):
    if node.name != 'Literal':
        sys.exit(42)
    
    # Check children to determine type.
    if node[0].name == 'DecimalIntegerLiteral':
        node.typ = Node('int')
    elif node[0].name == 'BooleanLiteral':
        node.typ = Node('boolean')
    elif node[0].name == 'CharacterLiteral':
        node.typ = Node('char')
    elif node[0].name == 'StringLiteral':
        node.typ = type_index['java.lang.String']
    else:
        node.typ = Node('null')

    return node.typ

