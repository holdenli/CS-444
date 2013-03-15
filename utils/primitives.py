from utils.node import Node

primitive_types = ['Int', 'Short', 'Char', 'Byte', 'Boolean', 'Null', 'Void']

primitive_dict = {k:Node(k) for k in primitive_types}

def get_type(name):
    if name not in primitive_types:
        return None 
    return primitive_dict[name]
    
def is_primitive(node):
    return node.name in primitive_types

def is_numeric(node):
    return node.name in ['Int', 'Short', 'Char', 'Byte']

def is_widening_conversion(node1, node2):
    # Define an order of "precedence", so that
    # a := b => bit_order[a] >= bit_order[b].
    bit_order = {
        'Int': 4,
        'Short': 3,
        'Char': 2,
        'Byte': 1,
    }
    return bit_order[node1.name] >= bit_order[node2.name]
 
