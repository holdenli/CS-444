from utils.node import Node
from utils.node import ASTNode

__typ_node = ASTNode('Type', None, [ASTNode('PrimitiveType', None,
    [ASTNode('Int')])])
__typ_node.canon = 'Int'
array_length_node = ASTNode("FieldDeclaration", None,
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
    # Define an order of "precedence", so that
    # a := b => bit_order[a] >= bit_order[b].
    bit_order = {
        'Int': 4,
        'Short': 3,
        'Char': 2,
        'Byte': 1,
    }
    return bit_order[type1] >= bit_order[type2]

