import os # File IO
import sys

import typecheck
import utils
from utils import class_hierarchy
from utils import logging

from codegen import statement
from codegen import class_layout
from codegen.codegen_info import CodegenInfo

class FileLayout:
    def __init__(self, canonical_type):
        self.canonical_type = canonical_type

        # List of member labels this file will import (extern).
        self.imports = []

        # List of member labels this file will export (global).
        self.exports = []

        # List of static fields' AST nodes.
        self.statics = []

        # List of constructors' AST nodes.
        self.constructors = []

        # List of methods' AST nodes.
        self.methods = []

        # AST node for the static int test() method. This is set if and only
        # if this is the first file.
        self.test = None

def gen(ast_list, class_index, type_index):
    # Preprocessing: generate a list of imports/exports for each file.
    file_layouts = build_file_layouts(ast_list, class_index)

    # For each of the FileLayouts, we import everything that's not exported.
    for i, current_layout in enumerate(file_layouts):
        for j, layout in enumerate(file_layouts):
            if i != j:
                current_layout.imports.extend(layout.exports)

    # "global" items.
    class_list = class_layout.build_class_list(class_index)
    constructor_index = class_layout.build_constructor_index(class_index)
    method_index = class_layout.build_method_index(class_index)
    field_index = class_layout.build_field_index(class_index)

    # Create output directory if it does not exist. If folder is not empty,
    # error.
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir) 
    if os.listdir(output_dir) != []:
        # logging.error('FATAL ERROR: Output directory not empty')
        # sys.exit(2) # Not a programming error or a compiler error... use 2?
        pass

    # Generate the code for the files.
    for i, layout in enumerate(file_layouts):
        # Info wrapper for passing stuff around.
        info = CodegenInfo(class_index[layout.canonical_type],
            class_index, type_index, class_list, constructor_index,
            method_index, field_index)

        filename = 'output/%s.s' % layout.canonical_type
        with open(filename, 'w') as f:
            gen_asm(f, layout, ast_list, info)

# This returns a list of file layouts for each AST (i.e., one FileLayout for
# each .java file).
def build_file_layouts(ast_list, class_index):
    layouts = []

    for i, ast in enumerate(ast_list):

        # TODO: get_class() is bad, use a different way to get canonical type
        class_obj = utils.ast.get_class(ast).obj
        canonical_type = class_obj.name

        file_layout = FileLayout(canonical_type)

        # Get labels for all static fields, constructors, and methods.
        # Add them to the appropriate list under file_layout.
        for member in class_obj.declare:

            # Static field.
            if isinstance(member, class_hierarchy.Field) and \
                'Static' in member.mods:
                member.node.label = get_static_field_label(member.node)
                file_layout.exports.append(member.node.label)
                file_layout.statics.append(member.node)

            elif isinstance(member, class_hierarchy.Method):
                # Constructor.
                if member.type == None:
                    member.node.label = get_method_label(member.node)
                    file_layout.exports.append(member.node.label)
                    file_layout.constructors.append(member.node)

                # Method, must not be abstract.
                elif member.type != None and 'Abstract' not in member.mods:
                    member.node.label = get_method_label(member.node)
                    file_layout.exports.append(member.node.label)
                    file_layout.methods.append(member.node)

                    # Check if it's static int test().
                    if i == 0 and member.name == 'test' and len(member.params) == 0:
                        file_layout.test = member.node

        # If we didn't find static int test() in the first file, bail.
        if i == 0 and file_layout.test == None:
            logging.error('Failed to find static int test() in first file')
            sys.exit(42)

        layouts.append(file_layout)

    return layouts

# Generates the .s file for the given file layout.
def gen_asm(f, file_layout, ast_list, info):
    canon_type = file_layout.canonical_type # Convenience.

    f.write('; %s\n' % file_layout.canonical_type)

    # List of labels for items we import.
    f.write('; Imports\n')
    for label in file_layout.imports:
        f.write('extern %s\n' % label)

    # List of labels for items we export.
    f.write('; Exports\n')
    for label in file_layout.exports:
        f.write('global %s\n' % label)
    f.write('\n')

    # List of SITs to import.
    f.write('; Selector index tables\n')
    for class_obj in info.class_list:
        if class_obj.name != canon_type:
            f.write('extern SIT~%s\n' % class_obj.name)
    f.write('global SIT~%s\n' % canon_type)
    f.write('\n')
    

    # List of SBMs to import.
    f.write('; Superclass binary matrix columns\n')
    for class_obj in info.class_list:
        if class_obj.name != canon_type:
            f.write('extern SBM~%s\n' % class_obj.name)
    f.write('global SIT~%s\n' % canon_type)
    f.write('\n')

    
    sit = class_layout.gen_sit(info.method_index, info.class_obj)
    for line in sit:
        f.write(line + '\n')
    sbm = class_layout.gen_sbm(info.class_list, info.class_obj)
    for line in sbm:
        f.write(line + '\n')

def lookup_by_decl(vars_dict, item):
    for (var_name, (i, var_decl)) in node.env.names.items():
        if item.obj == var_decl.obj and item.obj != None:
            return var_name

# Separating constructor stuff since we have to do other crap like initializing
# instance fields.
def gen_constructor(info, node):
    assert node.name == 'ConstructorDeclaration'
    output = []

    # Preamble for method.
    label = get_method_label(node)
    output.append("%s:" % label)

    # save ebp & esp
    output.extend([
        "push ebp",
        "mov ebp, esp",
    ])

    return output

def gen_method(info, node):
    assert node.name in 'MethodDeclaration'

    output = []

    # Preamble for method.
    label = get_method_label(node)
    output.append("%s:" % label)

    # save ebp & esp
    output.extend([
        "push ebp",
        "mov ebp, esp",
    ])

    # assign frame offsets to each parameter and
    # local variable declaration nodes
    start_index = len(node.find_child('Parameters').children) + 1
    for decl in node.find_child('Parameters'):
        decl.frame_offset = start_index
        start_index -= 1

    start_index = -1
    num_vars = 0
    for decl in find_nodes(Node('LocalVariableDeclaration')):
        decl.frame_offset = start_index
        start_index -= 1
        num_vars += 1

    # make room for local vars in the stack
    output.append("add esp, %d"  (num_vars*4))

    body = node[4] # methodbody or constructorbody
    if len(body.children) != 0:
        output.extend(gen_block(info, body[0], 0))

    # restore ebp & esp
    output.extend([
        "mov esp, ebp",
        "pop ebp"
    ])

    return output

def get_method_label(node):
    assert node.name in ['MethodDeclaration', 'ConstructorDeclaration']

    # Special case for native methods.
    # TODO: "in Joos 1W, all native methods must be static, must take a single
    # argument of type int, and must return a value of type int" should be
    # checked.

    class_name = node.obj.declared_in.name
    method_name = node.obj.name
    parameters = node.find_child('Parameters')
    param_types = []
    for param in parameters:
        if typecheck.is_array_type(param[0].canon) == True:
            # '[]'s replaced with '@', so that it can be accepted.
            param_types.append(param[0].canon[:-2] + '@')
        else:
            param_types.append(param[0].canon)

    label = ''

    # Natives methods are of the form:
    # NATIVE<canonical_type>.<method_name>
    if 'native' in node.modifiers: 
        label = 'NATIVE%s.%s' % (class_name, method_name)

    # Static methods are of the form:
    # STATICMETHOD~<canonical_type>.<method_name>~<param1>~<param2>...
    elif 'static' in node.modifiers:
        label = 'STATICMETHOD~%s.%s~%s' % (class_name, method_name, '~'.join(param_types))

    # Constructors are of the form:
    # CONSTRUCTOR~<canonical_type>.<method_name>~<param1>~<param2>...
    elif node.name == 'ConstructorDeclaration':
        label = 'CONSTRUCTOR~%s.%s~%s' % (class_name, method_name, '~'.join(param_types))

    # Instance methods are of the form:
    # METHOD~<canonical_type>.<method_name>~<param1>~<param2>...
    else:
        label = 'METHOD~%s.%s~%s' % (class_name, method_name, '~'.join(param_types))

    return label

def get_static_field_label(node):
    assert node.name == 'FieldDeclaration' and 'static' in node.modifiers

    class_name = node.obj.declared_in.name
    field_name = node.obj.name

    # Static fields are of the form:
    # STATICFIELD~<canonical_type>.<field_name>
    label = 'STATICFIELD~%s.%s' % (class_name, field_name)

    return label

