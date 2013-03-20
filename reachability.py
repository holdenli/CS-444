import sys
import logging
from utils import node
from utils import primitives
from utils.ast import *

# TODO: 15.28 Constant Expression is INCOMPLETE. FIX IT.

def reachability(node):
    method_bodys = []
    
    for m in get_constructors(node):
        z = m.find_child('Block')
        if z == None:
            # No constructor body?
            logging.error("FATAL ERROR: reachability: no constructor Block")
            sys.exit(1)
        method_bodys.append((z, m.obj.type))

    for m in get_methods(node):
        z = m.find_child('MethodBody')
        z = z.find_child('Block')
        if z == None:
            # No method body; not defined
            continue
        method_bodys.append((z, m.obj.type))

    for (m, t) in method_bodys:
        m.reachable = True
        statement_reachability(m, False)
        m.can_complete = True

        if m.will_end == False and t != 'Void' and t != None:
            logging.error("Missing return yo" + m.debug(1))
            sys.exit(42)
            
def statement_reachability(statement, return_expected):
    # Whoops, not actually reachable
    if statement.reachable != True:
        return False

    if statement.name == 'Block':
        statements = get_statement_children(statement)
        last_can_complete = True
        last_will_end = False
        for s in statements:
            if last_can_complete != True:
                logging.error("Not reachable bro: %s" % s)
                sys.exit(42)
            s.reachable = True
            statement_reachability(s, return_expected)
            last_can_complete = s.can_complete
            last_will_end = s.will_end
        if last_can_complete == True:
            statement.can_complete = True
        statement.will_end = last_will_end

    elif statement.name == 'LocalVariableDeclaration':
        # Also check definite assignment.
        verify_definite_assignment(statement)
        statement.can_complete = True
        statement.will_end = False

    elif statement.name == 'EmptyStatement' \
    or statement.name == 'ExpressionStatement':
        statement.can_complete = True
        statement.will_end = False 

    elif statement.name == 'ReturnStatement':
        statement.can_complete = False
        statement.will_end = True

    elif statement.name == 'IfStatement':
        if len(statement.children) == 2:
            statement[1].reachable = True
            statement_reachability(statement[1], return_expected)
            statement.can_complete = True
            statement.will_end = False
        else:
            statement[1].reachable = True
            statement[2].reachable = True
            statement_reachability(statement[1], return_expected)
            statement_reachability(statement[2], return_expected)
            if statement[1].can_complete == True \
            or statement[2].can_complete == True:
                statement.can_complete = True
            else:
                statement.can_complete = False
            statement.will_end = statement[1].will_end and statement[2].will_end

    elif statement.name == 'WhileStatement':
        expr = try_eval_expr(statement[0])
        s = statement[1]

        if expr != False:
            s.reachable = True
            statement_reachability(statement[1], return_expected)

        if expr == True:
            statement.can_complete = False
            if s.will_end == True:
                statement.will_end = True
            else:
                statement.will_end = None
        elif expr == False:
            logging.error("WhileStatement not reachable")
            sys.exit(42)
        else:
            statement.can_complete = True
            statement.will_end = False

    elif statement.name == 'ForStatement':
        # Check definite assignment in ForInit.
        if len(statement[0].children) == 1 and \
            statement[0][0].name == 'LocalVariableDeclaration':
            verify_definite_assignment(statement[0][0])

        expr = None
        s = statement[3][0]
        if len(statement[1].children) == 0:
            expr = True
        else:
            expr = try_eval_expr(statement[1][0])

        if expr != False:
            s.reachable = True 
            statement_reachability(s, return_expected)
            if s.will_end == True:
                statement.will_end = True
            else:
                statement.will_end = None

        if expr == True:
            statement.can_complete = False
        elif expr == False:
            logging.error("ForStatement not reachable")
            sys.exit(42)
        else:
            statement.can_complete = True
            statement.will_end = False

    else:
        logging.error("FATAL ERROR: statement_reachability")
        sys.exit(1)

# fuck, fix this.
# Returns True or False if it is a constant expression (None otherwise)
def try_eval_expr(node):
    if node.name == 'Literal':
        if node[0].name == 'BooleanLiteral':
            return node[0].value.value == "true"
        elif node[0].name == 'DecimalIntegerLiteral':
            return int(node[0].value.value)
        else:
            pass # TODO STRINGS AND SHIT FUCK
    elif node.name == 'ConditionalOrExpression':
        expr1 = try_eval_expr(node[0])
        expr2 = try_eval_expr(node[2])
        if expr1 != None and expr2 != None:
            ret = expr1 == True or expr2 == True
            return ret
    elif node.name == 'ConditionalAndExpression':
        expr1 = try_eval_expr(node[0])
        expr2 = try_eval_expr(node[2])
        if expr1 != None and expr2 != None:
            ret = expr1 == True and expr2 == True
            return ret
    elif node.name == 'EqualityExpression':
        expr1 = None
        expr2 = None
        if node[0].typ == 'Boolean' or primitives.is_numeric(node[0].typ):
            expr1 = try_eval_expr(node[0])
            expr2 = try_eval_expr(node[2])
            if expr1 != None and expr2 != None:
                if node[1].name == 'EqualOperator':
                    return expr1 == expr2
                else:
                    return expr1 != expr2
            else:
                return None
        else:
            return None
    elif node.name == 'RelationalExpression':
        expr1 = None
        expr2 = None
        if primitives.is_numeric(node[0].typ):
            expr1 = try_eval_expr(node[0])
            expr2 = try_eval_expr(node[2])
            if expr1 != None and expr2 != None:
                if node[1].name == 'LessThanOperator':
                    return expr1 < expr2
                elif node[1].name == 'GreaterThanOperator':
                    return expr1 > expr2
                elif node[1].name == 'LessThanEqualOperator':
                    return expr1 <= expr2
                elif node[1].name == 'GreaterThanEqualOperator':
                    return expr1 >= expr2
            else:
                return None
    elif node.name == 'AdditiveExpression':
        expr1 = None
        expr2 = None
        if primitives.is_numeric(node[0].typ):
            expr1 = try_eval_expr(node[0])
            expr2 = try_eval_expr(node[2])
            if expr1 != None and expr2 != None:
                if node[1].name == 'AddOperator':
                    return expr1 + expr2
                elif node[1].name == 'SubtractOperator':
                    return expr1 - expr2
            else:
                return None
    elif node.name == 'MultiplicativeExpression':
        expr1 = None
        expr2 = None
        if primitives.is_numeric(node[0].typ):
            expr1 = try_eval_expr(node[0])
            expr2 = try_eval_expr(node[2])
            if expr1 != None and expr2 != None:
                if node[1].name == 'MultiplyOperator':
                    return expr1 * expr2
                elif node[1].name == 'DivideOperator':
                    return expr1 / expr2
                elif node[1].name == 'ModuloOperator':
                    return None # TODO WHAT MODULO TOO HARD I GIVE UP - Holden
            else:
                return None
    elif node.name == 'UnaryExpression':
        # TODO FUUUUUUUUUUUUUUUUU
        pass
    elif node.name == 'CastExpression':
        return try_eval_expr(node[1])
    elif node.name == 'PostfixExpression':
        return try_eval_expr(node[0])

    return None

def verify_definite_assignment(node):
    if node.name != 'LocalVariableDeclaration':
        logging.error('FATAL ERROR: verify_definite_assignment()')

    if len(node[2].children) == 0:
        logging.error('Local variable declaration must have initializer.')
        sys.exit(42)

    # See if it references itself in its initializer.
    for name_node in node[2][0].select(['Name']):
        if name_node.decl != None and name_node.decl is node:
            logging.error('Local variable initialization cannot self-reference.')
            sys.exit(42)

