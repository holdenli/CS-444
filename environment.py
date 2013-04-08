
import sys

from utils.node import Node, ASTNode
from utils.node import find_nodes
from utils import logging
from scanner import Token

class Environment(Node):
    """
        this class has a mess of different member variables..
        each environment name employes a different set of member variables, so
        use contextually.


        self.names is a dictionary of string -> Node
        where the string is the name of the variable in the environment's scope,
        and node is the declaration of that variable

        self.methods and self.fields are only defined for the Class environment;
        they are a method/field name->declaration mapping.

        self.value used in PackageDeclaration and ClassDeclaration, and it
        represents the name of the package or class

        self.parent is used in ClassDeclaration, and points to the parent/super
        ClassDeclaration environment
    """

    def __init__(self, name=None, value=None,
        node=None, children=None, names=None,
        parent=None):

       # dictionary of names -> declarations
       # a declaration is just the reference to the Node
       if names == None:
           names = {}
       if children == None:
           children = []

       self.names = names

       self.name = name
       self.value = value
       self.node = node

       self.fields = {}
       self.methods = {}

       self.parent = parent

       self.children = children

       # canonical name of Compulation Unit
       self.canon = None

    def __repr__(self):
        return '<Env: %s=%s Node=%s> %s' % (self.name, self.value, self.node, self.names)

    def __getitem__(self, key):
        children = [c for c in self.children if c.name == key]
        if len(children) == 0:
            return None
        elif len(children) == 1:
            return children[0]
        else:
            return children

    def __eq__(self, o):
        return (self.__class__ == o.__class__) and (self.name == o.name)

def env_type_node(env):
    cls = env['ClassDeclaration']
    iface = env['InterfaceDeclaration']
    if cls:
        return cls.node
    elif iface:
        return iface.node
    else:
        return None

def env_type_name(env):

    cls = env['ClassDeclaration']
    iface = env['InterfaceDeclaration']

    if cls:
        return cls.node.find_child('ClassName').leaf_values()[0]
    elif iface:
        return iface.node.find_child('InterfaceName').leaf_values()[0]
    else:
        return None

def build_environments(ast_list):
    # index of packages;  package -> list of compilation units
    # index of canonical named types;  canonical name -> compilation unit
    pkg_index = {}

    for ast in ast_list:
        pkg_env = build_environment(ast)

        pkg_name = pkg_env.value
        if pkg_name not in pkg_index:
            pkg_index[pkg_name] = []
    
        if pkg_env.children:
            pkg_index[pkg_name].append(pkg_env.children[0])

    return pkg_index

def build_environment(root_ast):
    """
        environment stack:

        - PackageDeclaration
        - CompilationUnit
            - TypeImports
            - PackageImports
    """

    abs_tree = root_ast.find_child('CompilationUnit')

    pkg = list(abs_tree.select(['PackageDeclaration']))
    pkg_name = ''
    if len(pkg) == 0 or len(pkg[0].children) == 0:
        # default package name
        pkg = Node(name='PackageDeclaration', children=[
            Node(name='Identifier', value=Token(label='Identifier',
            value='MAIN_PKG', pos=-1, line=-1))
        ])
        pkg_name = 'MAIN_PKG'
    else:
        pkg = pkg[0]
        pkg_name = '.'.join(pkg.select_leaf_values(['Identifier']))

    # add the package to the environment
    pkg_env = Environment(name='PackageDeclaration', node=pkg,
        value='.'.join([l.value.value for l in pkg.leafs()])
        )
    pkg.env = pkg_env # link the node back to here
    
    cu_node = list(abs_tree.select(['CompilationUnit']))
    if len(cu_node) != 1:
        return pkg_env
    cu = Environment(name='CompilationUnit', node=cu_node[0])
    cu_node[0].env = cu

    # add type imports to CompilationUnit
    ti = {}
    for i in abs_tree.select(['TypeImports', 'ImportDeclaration']):
        i_name = '.'.join(n.value.value for n in i.leafs())

        ti[i_name] = i

    ti_node = list(abs_tree.select(['TypeImports']))[0]
    ti_env = Environment(name='TypeImport', node=ti_node,
                         names=ti)
    cu.children.append(ti_env)
    ti_node.env = ti_env

    # add package imports to CompilationUnit
    pi = {}
    for i in abs_tree.select(['PackageImports', 'ImportDeclaration']):
        p_name = '.'.join(n.value.value for n in i.leafs())
        pi[p_name] = i
   
    # also add the package name itself into the package imports
    pi[pkg_name] = pkg

    pi_node = list(abs_tree.select(['PackageImports']))[0]
    pi_env = Environment(name='PackageImports', node=pi_node,
                         names=pi)
    cu.children.append(pi_env)
    pi_node.env = pi_env

    # add a class or interface to the package
    type_name = ''
    cls = abs_tree.find_child('ClassDeclaration')
    iface = abs_tree.find_child('InterfaceDeclaration')
    if cls != None:
        cu.children.append(build_class_env(cls))
        type_name = cls.find_child('ClassName').leaf_values()[0]
    if iface != None:
        cu.children.append(build_interface_env(iface))
        type_name = iface.find_child('InterfaceName').leaf_values()[0]

    # add the CompilationUnit to the package
    cu.canon = '%s.%s' % (pkg_name, type_name)

    pkg_env.children.append(cu)

    return pkg_env

def build_method_params(method_node):
    params = {}
    for p in method_node.select(['Parameters', 'Parameter']):
        param_name = p[1].value.value
        if param_name in params:
            logging.error('Two params=%s have cannot have the same name'
                % (param_name))
            sys.exit(42)
        
        params[param_name] = p
    return params

def build_class_env(cls_node):
    """
        returns a class environment
    """
    # builds properties
    (fields, methods) = build_member_props(cls_node)

    # class Environment
    env = Environment(name='ClassDeclaration', node=cls_node)
    env.value = cls_node.select_leaf_values(['ClassDeclaration', 'ClassName', 'Identifier'])[0]
    env.names = fields
    env.fields = fields
    env.methods = methods
    env.children = []

    cls_node.env = env

    # each child environment represents a method's environment
    for method_name in methods:
        for method_node in methods[method_name]:

            # MethodDecl's children = [Modifiers, Type, ..]
            method_env = Environment('MethodDeclaration', node=method_node)
            method_node.env = method_env
            
            # method_env.value = method name
            method_env.value = method_node.find_child('Identifier').value.value
           
            # get the parameters
            params = build_method_params(method_node)

            block_env = build_block_env(method_node, set(params))

            if len(block_env) > 0:
                # add the params into the root method_env
                block_env[0].names.update(params)
                method_env.children.append(block_env[0])

            env.children.append(method_env)

    return env

def build_interface_env(iface_node):
    # builds properties
    (fields, methods) = build_member_props(iface_node)

    # class Environment
    env = Environment(name='InterfaceDeclaration', node=iface_node)
    env.value = iface_node.select_leaf_values(['InterfaceDeclaration', 'InterfaceName'])[0]
    env.names = fields
    env.fields = fields
    env.methods = methods
    env.children = []

    iface_node.env = env

    return env

def build_member_props(tree):
    fields = {}
    methods = {}

    # build fields
    for field in tree.select(['Fields', 'FieldDeclaration']):
        f = list(field.select(['FieldDeclaration',
            'Identifier']))[0].value.value
        
        field.modifiers = set(field.find_child('Modifiers').leaf_values())

        if f in fields:
            logging.error("No two fields=%s declared in the same class may have the same name." % f)
            sys.exit(42)
        
        fields[f] = field

    # build constructors
    for cons in tree.select(['Constructors', 'ConstructorDeclaration']):
        c = cons.find_child('Identifier').leaf_values()[0]
        cons.modifiers = set(cons.find_child('Modifiers').leaf_values())

        if c not in methods:
            methods[c] = []
        methods[c].append(cons)

    # build methods
    for meth in tree.select(['Methods', 'MethodDeclaration']):

        m = meth.find_child('Identifier').leaf_values()[0]
        meth.modifiers = set(meth.find_child('Modifiers').leaf_values())

        if m not in methods:
            methods[m] = []
        methods[m].append(meth)

    return (fields, methods)

def build_block_env(tree, carry, new_block=True):
    """
        returns a list of environments
        sub-environments are recursively generated
    """
    envs = []

    for block in find_nodes(tree, [Node('Block'), Node('ForStatement')]):
        # get all the variables in this environment
        env = Environment(name='Block')
        env.node = block
        block.env = env # the block should point back to the env
        
        new_carry = set(carry)

        if block.name == 'ForStatement':
            if new_block:
                env.children.extend(build_block_env(ASTNode(children=[block]),
                    new_carry, new_block=False))
            else:
                # block[0] is ForInit
                # block[0][0] is LocalVariableDeclaration
                # block[0][0][1] is Identifier for LocalVariableDecl
                # block[3] is ForBody
                for_vars = list(block.select(['ForStatement', 'ForInit',
                    'LocalVariableDeclaration']))

                if len(for_vars) != 0 and block[0][0] == Node('LocalVariableDeclaration'):
                    name = for_vars[0][1].value.value
                    if name in new_carry:
                        logging.error("No two local variables=%s with overlapping scope have the same name"
                            % name)
                        sys.exit(42)

                    env.names[name] = for_vars[0]
                    new_carry.add(name)

                env.children.extend(build_block_env(block[3], new_carry))
        else:

            for stmt in find_nodes(block, [Node('Block'),
                Node('ForStatement'),
                Node('LocalVariableDeclaration')]):

                # are we making a new block?
                if stmt == Node('Block') or stmt == Node('ForStatement'):
                    env.children.extend(
                        build_block_env(Node(children=[stmt]), new_carry))

                # are we declaring a variable?
                elif stmt == Node('LocalVariableDeclaration'):
                    name = list(stmt.select(['LocalVariableDeclaration', 'Identifier']))
                    name = name[0].value.value
                    if name in new_carry:
                        logging.error("No two local variables=%s with overlapping scope have the same name"
                            % name)
                        sys.exit(42)

                    env.names[name] = stmt
                    new_carry.add(name)
                       
        envs.append(env)

    return envs


