from utils.node import Node
from utils.node import ASTNode

__typ_node = ASTNode('Type', None, [ASTNode('PrimitiveType', None,
    [ASTNode('Int')])])
__typ_node.canon = 'Int'
array_length_node = ASTNode("FakeFieldDeclaration", None,
    [ASTNode('Modifiers'), __typ_node, ASTNode('Identifier'),
        ASTNode('Initializer')])

primitive_types = ['Int', 'Short', 'Char', 'Byte', 'Boolean', 'Null', 'Void']

def is_primitive(canon_type):
    return canon_type in primitive_types

def is_numeric(canon_type):
    return canon_type in ['Int', 'Short', 'Char', 'Byte']

def is_reference(canon_type):
    return not (is_primitive(canon_type)) and isinstance(canon_type, str)

def is_widening_conversion(type1, type2):
    if type1 == type2:
        return True

    elif type2 == 'Byte':
        return type1 == 'Short' or type1 == 'Int'

    elif type2 == 'Short':
        return type1 == 'Int'

    elif type2 == 'Char':
        return type1 == 'Int'

