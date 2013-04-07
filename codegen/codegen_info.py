from utils import logging

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
        label = '__jump' + self.jump_counter
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

        field_name = node.find_child("FieldName")[0].value.value

        field = Temp_Field(field_name)

        offset = self.field_index[self.class_obj.name].index(field) * 4
        return offset

    def get_method_offset(self, node):
        if node.name != "MethodInvocation":
            logging.error("get_method_offset")
            sys.exit(1)

        method_name = node.find_child("MethodName")[0].value.value
        params = []
        for child in node.find_child("Arguments").children:
            params.append(child.typ)
        
        method = Temp_Method(method_name, params)

        offest = self.method_index.index(method) * 4
        return offset

