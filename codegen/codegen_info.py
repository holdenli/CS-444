from utils import logging
from utils import class_hierarchy

#
# One of these created for each file to assist with passing info around in
# code generation methods.
#
class CodegenInfo:
    def __init__(self, class_obj, class_index, type_index, class_list,
        constructor_index, method_index, field_index):
        # Canonical type for this file.
        self.class_obj = class_obj

        # All the "global" items we will need to refer to.
        self.class_index = class_index
        self.type_index = type_index

        self.class_list = class_list
        self.constructor_index = constructor_index
        self.method_index = method_index
        self.field_index = field_index

        # var_name -> (index, node_decl)
        self.local_vars = {}

        # Counter for local jumps (not exported).
        self.jump_counter = 0

    def get_jump_label(self):
        label = '__jump' + str(self.jump_counter)
        self.jump_counter += 1
        return label

    # get the size of an instance of a type in bytes
    def get_size(self, canon_type):
        if canon_type in ["Boolean", "Byte", "Char", "Int", "Short"]:
            return 4
        
        object_overhead_bytes = 3*4 # SIT, SBM, Array flag
        return object_overhead_bytes + len(self.field_index[canon_type])*4

    def get_field_offset(self, node):
        if node.name != "FieldAccess":
            logging.error("get_field_offset")
            sys.exit(1)

        receiver_type = node.find_child("FieldReceiver")[0].typ
        field_name = node.find_child("FieldName")[0].value.value

        return self.get_field_offset_from_field_name(receiver_type, field_name)

    def get_field_offset_from_field_name(self, receiver_type, field_name):
        field = class_hierarchy.Temp_Field(field_name)

        field_list = self.field_index[receiver_type]
        offset = field_list.index(field) * 4
        return offset

    def get_method_offset(self, node):
        if node.name != "MethodInvocation":
            logging.error("get_method_offset")
            sys.exit(1)

        method_name = node.find_child("MethodName")[0].value.value
        params = []
        for child in node.find_child("Arguments").children:
            params.append(child.typ)
        
        method = class_hierarchy.Temp_Method(method_name, params)

        offset = self.method_index.index(method) * 4
        return offset

