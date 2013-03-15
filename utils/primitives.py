from utils import node

primitive_types = ['int', 'short', 'char', 'byte', 'boolean', 'null']

primitive_dict = {k:node.Node(k) for k in primitive_types}

def get_type(name):
    if name not in primitive_types:
        return None 
    return primitive_dict[name]
    
def is_primitive(type_node):
    return (node.name in primitive_types)

