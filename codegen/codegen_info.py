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

