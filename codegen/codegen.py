import os # File IO
import sys
import shutil # rmtree

import typecheck
import utils
from utils import class_hierarchy
from utils import logging
from utils.options import JooscOptions

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

        # List of other types.
        self.other_types = []

        # AST node for the static int test() method. This is set if and only
        # if this is the first file.
        self.test = None

# Convenience wrapper for file. Access member f for the file if needed.
class FileHelper:
    def __init__(self, f):
        self.f = f

    def comment(self, cmt):
        self.f.write('; %s\n' % cmt)

    def write(self, txt):
        self.f.write(txt + '\n')

    def newline(self):
        self.f.write('\n')

    def writelines(self, lines):
        for line in lines:
            self.f.write(line + '\n')

# Main code generation function called by Joosc.
def gen(options, ast_list, class_index, type_index):
    # Preprocessing: generate a list of imports/exports for each file.
    file_layouts = build_file_layouts(ast_list, class_index)

    # For each of the FileLayouts, we import everything that's not exported.
    for i, current_layout in enumerate(file_layouts):
        for j, layout in enumerate(file_layouts):
            if i != j:
                current_layout.imports.extend(layout.exports)
                current_layout.other_types.append(layout.canonical_type)

    # "global" items.
    class_list = class_layout.build_class_list(class_index)
    constructor_index = class_layout.build_constructor_index(class_index)
    method_index = class_layout.build_method_index(class_index)
    field_index = class_layout.build_field_index(class_index)

    # Create output directory if it does not exist. If folder is not empty,
    # error.
    output_dir = 'output'
    if options.clean_output == True: # Nuke the directory if specified.
        shutil.rmtree(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if os.listdir(output_dir) != []:
        #logging.error('FATAL ERROR: Output directory not empty')
        #sys.exit(2) # Not a programming error or a compiler error... use 2?
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

    # Copy the stdlib runtime.s file.
    #shutil.copyfile('lib/stdlib/5.1/runtime.s', '%s/runtime.s' % output_dir)

    # Utility files.
    with open('%s/misc.s' % output_dir, 'w') as f:
        output = class_layout.gen_sbm_primitives(class_list)
        for line in output:
            f.write(line + '\n')

# This returns a list of file layouts for each AST (i.e., one FileLayout for
# each .java file).
def build_file_layouts(ast_list, class_index):
    layouts = []
    found_test_method = False

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
                file_layout.statics.append(member)

            elif isinstance(member, class_hierarchy.Method):
                # Constructor.
                if member.type == None:
                    member.node.label = get_method_label(member.node)
                    file_layout.exports.append(member.node.label)
                    file_layout.constructors.append(member)

                # Method, must not be abstract.
                elif member.type != None and 'Abstract' not in member.mods:
                    member.node.label = get_method_label(member.node)

                    # Code for native methods are found elsewhere, so don't
                    # export.
                    if 'Native' not in member.mods:
                        file_layout.exports.append(member.node.label)
                        file_layout.methods.append(member)

                    # Check if it's static int test().
                    if 'Static' in member.mods and \
                        member.name == 'test' and \
                        len(member.params) == 0:
                        if found_test_method:
                            logging.error('More than one static init test() found')
                            sys.exit(42)
                        else:
                            file_layout.test = member
                            found_test_method = True

        # If we didn't find static int test() in the first file, bail.
        if i == 0 and not found_test_method:
            logging.error('Failed to find static int test() in first file')
            sys.exit(42)

        layouts.append(file_layout)
    
    return layouts

# Generates the .s file for the given file layout.
# Convention: This is the only file that deals with writing to files.
def gen_asm(f, file_layout, ast_list, info):
    h = FileHelper(f)
    canon_type = file_layout.canonical_type # Convenience.

    h.write('section .text')

    h.comment(file_layout.canonical_type)

    h.newline()

    # If this is the "main" file, export __start.
    if file_layout.test != None:
        h.write('global _start')

    # SBM for primitive types.
    h.write('extern SBM~@Boolean')
    h.write('extern SBM~@Byte')
    h.write('extern SBM~@Char')
    h.write('extern SBM~@Int')
    h.write('extern SBM~@Short')

    h.newline()

    # Runtime calls.
    h.write('extern __malloc')
    h.write('extern __exception')
    h.write('extern NATIVEjava.io.OutputStream.nativeWrite')

    # List of labels for items we import.
    h.comment('Imports')
    for label in file_layout.imports:
        h.write('extern %s' % label)

    # List of labels for items we export.
    h.comment('Exports')
    for label in file_layout.exports:
        h.write('global %s' % label)

    h.newline()

    # List of SITs to import. Also export the SIT of this class.
    h.comment('Selector index tables')
    for class_obj in info.class_list:
        if class_obj.name != canon_type:
            h.write('extern SIT~%s' % class_obj.name)
    h.write('global SIT~%s' % canon_type)

    h.newline()

    # List of SBMs to import. Also export the SBM of this class.
    h.write('; Superclass binary matrix columns')
    for class_obj in info.class_list:
        if class_obj.name != canon_type:
            h.write('extern SBM~%s' % class_obj.name)
    h.write('global SBM~%s' % canon_type)

    h.newline()

    # Assembly code for the selector index table.
    sit_code = class_layout.gen_sit(info.method_index, info.class_obj)
    h.writelines(sit_code)

    h.newline()

    # Assembly code for the superclass binary matrix.
    sbm_code = class_layout.gen_sbm(info.class_list, info.class_obj)
    h.writelines(sbm_code)

    h.newline()

    # Generate methods.
    for method_obj in file_layout.methods:
        method_code = gen_method(info, method_obj)
        h.writelines(method_code)

    # Generate constructors.
    for constructor_obj in file_layout.constructors:
        constructor_code = [(constructor_obj.node.label + ':'), "ret"]
        #constructor_code = gen_constructor(info, constructor_obj)
        h.writelines(constructor_code)

    # Generate static initialization.
    static_init_code = gen_static_init(info, file_layout)
    h.writelines(static_init_code)

    # Generate _start stuff if necessary.
    if file_layout.test != None:
        start_code = gen_start(info, file_layout)
        h.writelines(start_code)

    h.write('section .data')

    # Generate static fields.
    for static_field_obj in file_layout.statics:
        h.write(static_field_obj.node.label + ':')
        h.write('dd 0')

def lookup_by_decl(vars_dict, item):
    for (var_name, (i, var_decl)) in node.env.names.items():
        if item.obj == var_decl.obj and item.obj != None:
            return var_name

# Separating constructor stuff since we have to do other crap like initializing
# instance fields.
def gen_constructor(info, constructor_obj):
    node = constructor_obj.node
    assert node.name == 'ConstructorDeclaration'

    # Preprocessing:
    # Assign frame pointer offsets to each parameter and local variable
    # declaration node.
    param_start_index = len(node.find_child('Parameters').children) + 1
    for decl in node.find_child('Parameters'):
        decl.frame_offset = param_start_index
        param_start_index -= 1

    local_var_start_index = -1
    num_vars = 0
    for decl in utils.node.find_nodes(node, utils.node.Node('LocalVariableDeclaration')):
        decl.frame_offset = local_var_start_index
        local_var_start_index -= 1
        num_vars += 1
    output = []

    # Preamble for constructor.
    output.append(constructor_obj.node.label + ':')

    # save ebp & esp
    output.extend([
        "push ebp",
        "mov ebp, esp",
    ])
    # make room for local vars in the stack
    output.append("sub esp, %d" % (num_vars*4))

    # Initialize instance fields.
    for field_obj in info.field_index[info.class_obj.name]:
        field_node = field_obj.node
        if 'Static' not in field_obj.mods and \
            len(field_node[3].children) == 1: # Initializer

            # Evaluate initializer.
            output.extend(expression.gen_expr(field_node[3][0])

            # Get the address of 'this'.
            this_offset = (len(constructor_obj.params) * 4) + 8 
            output.append('mov ebx, ebp')
            output.append('add ebx, %d' % this_offset)
            output.append('mov ebx, [ebx]')

            # Assign to field offset.
            field_name = field_obj.name
            field_offset = info.get_field_offset_from_field_name(field_name):
            output.append('mov [ebx+%d], eax' % field_offset)

    body = node[4] # ConstructorBody
    if len(body.children) != 0:
        output.extend(statement.gen_block(info, body[0], constructor_obj))

    # restore ebp & esp
    output.extend([
        "END~%s:" % (constructor_obj.node.label),
        "mov esp, ebp",
        "pop ebp",
        "ret"
    ])

    return output

def gen_method(info, method_obj):
    node = method_obj.node
    assert node.name in 'MethodDeclaration'

    # Preprocessing:
    # Assign frame pointer offsets to each parameter and local variable
    # declaration node.
    param_start_index = len(node.find_child('Parameters').children)
    for decl in node.find_child('Parameters').children:
        decl.frame_offset = param_start_index
        param_start_index -= 1

    local_var_start_index = -1
    num_vars = 0
    for decl in utils.node.find_nodes(node, utils.node.Node('LocalVariableDeclaration')):
        decl.frame_offset = local_var_start_index
        local_var_start_index -= 1
        num_vars += 1

    output = []

    # Preamble for method.
    output.append(method_obj.node.label + ':')

    # save ebp & esp
    output.extend([
        "push ebp",
        "mov ebp, esp",
    ])
    # make room for local vars in the stack
    output.append("sub esp, %d" % (num_vars*4))

    body = node[4] # MethodBody
    if len(body.children) != 0:
        output.extend(statement.gen_block(info, body[0], method_obj))

    # restore ebp & esp
    output.extend([
        "END~%s:" % (method_obj.node.label),
        "mov esp, ebp",
        "pop ebp",
        "ret"
    ])

    return output

# Generates the code for static initialization in this file.
def gen_static_init(info, file_layout):
    output = []

    static_init_lbl = get_static_init_label(file_layout.canonical_type)
    output.append('global ' + static_init_lbl)
    output.append(static_init_lbl + ':')

    # Do stuff.
    for static_field_obj in file_layout.statics:
        node = static_field_obj.node
        output.extend(statement.gen_static_field_decl(info, node))

    # Return to caller.
    output.append('ret')

    return output

# Generates the code for the _start label.
# This basically does static field initialization for each class, and calls the
# static int test() method.
def gen_start(info, file_layout):
    output = []

    # Import all the static initialization labels of the other types.
    for other_type in file_layout.other_types:
        output.append('extern %s' % get_static_init_label(other_type))

    output.append('_start:')

    # Call call the static initialization labels.
    output.append('call %s' % get_static_init_label(file_layout.canonical_type))
    for other_type in file_layout.other_types:
        output.append('call %s' % get_static_init_label(other_type))

    # Call static int test().
    # The return value of test() is in eax.
    output.append('call %s' % file_layout.test.node.label)

    # Exit. Return code goes into ebx, 1 goes into eax.
    output.append('mov ebx, eax')
    output.append('mov eax, 0x1')
    output.append('int 0x80')

    return output

#
# Helpers for generating labels.
#

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


def get_static_init_label(canonical_type):
    # Static initialition labels are of the form:
    # STATICINIT~<canonical_type>
    return 'STATICINIT~%s' % canonical_type

