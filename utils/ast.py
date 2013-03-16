#!/usr/bin/python3

import logging
from utils.node import *

def get_class(n):
    z = list(n.select(["ClassDeclaration"])) + list(n.select(["InterfaceDeclaration"]))
    if len(z) != 1:
        return None

    return z[0]

def get_fields(n):
    if get_class(n) == None:
        return None

    z = list(n.select(["FieldDeclaration"]))
    
    return z

def get_constructors(n):
    if get_class(n) == None:
        return None

    z = list(n.select(["ConstructorDeclaration"]))
    
    return z

def get_methods(n):
    if get_class(n) == None:
        return None

    z = list(n.select("MethodDeclaration"))
    
    return z

def get_exprs(n):
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

    return exprs


