
import sys

from utils.node import Node
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

    """

    def __init__(self, name=None, value=None,
        node=None, children=None, names=None):

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

       self.children = children

    def __repr__(self):
        return '<Env: %s> %s' % (self.name, self.names)

    def __getitem__(self, key):
        return

def build_environments(ast_list):
    # index of packages;  package -> list of compilation units
    # index of canonincal named types;  canonical name -> type
    pkg_index = {}
    type_index = {}

    for ast in ast_list:
        pkg_env = build_environment(ast)

        pkg_name = pkg_env.value
        if pkg_name not in pkg_index:
            pkg_index[pkg_name] = []
        
        pkg_index[pkg_name].append(pkg_env.children[0])

        # get canonical name of the type from this compilation unit
        type_env = pkg_env.children[0].children[2]
        type_name = type_env.value
        canon_name = '%s.%s' % (pkg_name, type_name)

        if canon_name in type_index:
            logging.error("No two classes or interfaces have the same canonical name=%s" % canon_name )
            sys.exit(42)
        type_index[canon_name] = type_env

        pkg_env.pprint()



def build_environment(abs_tree):
    """
        environment stack:

        - PackageDeclaration
        - CompilationUnit
            - TypeImports
            - PackageImports
    """

    pkg = list(abs_tree.select(['PackageDeclaration']))
    if len(pkg[0].children) == 0:
        # default package name
        pkg = Node(name='PackageDeclaration', children=[
            Node(name='Identifier', value=Token(label='Identifier',
            value='MAIN_PKG', pos=-1, line=-1))
        ])
    else:
        pkg = pkg[0]

    # add the package to the environment
    pkg_env = Environment(name='PackageDeclaration', node=pkg,
        value='.'.join([l.value.value for l in pkg.leafs()])
        )
    
    cu_node = list(abs_tree.select(['CompilationUnit']))
    if len(cu_node) != 1:
        return pkg_env
    cu = Environment(name='CompilationUnit', node=cu_node[0])

    # add type imports to CompilationUnit
    ti = {}
    for i in abs_tree.select(['TypeImports', 'ImportDeclaration']):
        pkg = '.'.join(n.value.value for n in i.leafs())
        ti[pkg] = i

    ti_node = list(abs_tree.select(['TypeImports']))[0]
    cu.children.append(Environment(name='TypeImport',
        node=ti_node,
        names=ti))

    # add package imports to CompilationUnit
    pi = {}
    for i in abs_tree.select(['PackageImports', 'ImportDeclaration']):
        pkg = '.'.join(n.value.value for n in i.leafs())
        pi[pkg] = i

    pi_node = list(abs_tree.select(['PackageImports']))[0]
    cu.children.append(Environment(name='PackageImports',
        node=pi_node,
        names=pi))

    # add a class or interface to the package
    cls = list(abs_tree.select(['ClassDeclaration']))
    iface = list(abs_tree.select(['InterfaceDeclaration']))
    if len(cls) > 0:
        cu.children.append(build_class_env(cls[0]))
    if len(iface) > 0:
        cu.children.append(build_interface_env(iface[0]))

    # add the CompilationUnit to the package
    pkg_env.children.append(cu)

    return pkg_env

def build_class_env(cls_node):
    """
        returns a class environment
    """
    # builds properties
    (fields, methods) = build_type_props(cls_node)

    # class Environment
    env = Environment(name='ClassDeclaration', node=cls_node)
    env.value = cls_node.select_leaf_values(['ClassDeclaration', 'ClassName', 'Identifier'])[0]
    env.names = fields
    env.fields = fields
    env.methods = methods
    env.children = []

    # each child environment represents a method's environment
    for method_name in methods:
        for method_node in methods[method_name]:

            # get the parameters
            params = {}
            for p in method_node.select(['MethodDeclaration', 'Parameters',
                'Parameter']):
                param_name = p[1].value.value
                if param_name in params:
                    logging.error('Two params=%s have cannot have the same name'
                        % (param_name))
                    sys.exit(42)
                
                params[param_name] = p

            method_env = build_block_env(method_node, set(params))
            if len(method_env) > 0:
                # add the params into the root method_env
                method_env[0].names.update(params)
                env.children.extend(method_env)

    return env

def build_interface_env(iface_node):
    # builds properties
    (fields, methods) = build_type_props(iface_node)

    # class Environment
    env = Environment(name='InterfaceDeclaration', node=iface_node)
    env.value = iface_node.select_leaf_values(['InterfaceDeclaration', 'InterfaceName'])[0]
    env.names = fields
    env.fields = fields
    env.methods = methods
    env.children = []

    return env

def build_type_props(tree):
    fields = {}
    methods = {}

    # build fields
    for field in tree.select(['Fields', 'FieldDeclaration']):
        f = list(field.select(['FieldDeclaration',
            'Identifier']))[0].value.value

        if f in fields:
            logging.error("No two fields=%s declared in the same class may have the same name." % f)
            sys.exit(42)
        
        fields[f] = field

    # build constructors
    for cons in tree.select(['Constructors', 'ConstructorDeclaration']):
        c = list(cons.select(['ConstructorDeclaration',
            'Identifier']))[0].value.value

        if c not in methods:
            methods[c] = []
        methods[c].append(cons)

    # build methods
    for meth in tree.select(['Methods', 'MethodDeclaration']):
        m = list(meth.select(['MethodDeclaration',
            'Identifier']))[0].value.value

        if m not in methods:
            methods[m] = []
        methods[m].append(meth)

    return (fields, methods)

def build_block_env(tree, carry):
    """
        returns a list of environments
        sub-environments are recursively generated
    """
    envs = []
    blocks = list(tree.select(['Block'], inclusive=False))
    for block in blocks:

        # get all the variables in this environment
        env = Environment(name='Block')
        env.node = block

        new_carry = set(carry)

        for var in build_variables(block):
            name = list(var.select(['LocalVariableDeclaration', 'Identifier']))
            name = name[0].value.value

            # variables same name in an overlapping scope?
            if name in carry:
                logging.error("No two local variables=%s with overlapping scope have the same name"
                    % name)
                sys.exit(42)

            env.names[name] = var
            new_carry.add(name)
        
        # look for subenvs in this environment:
        env.children.extend(build_block_env(block, new_carry))
        envs.append(env)

    return envs

def build_variables(block_tree):
    # we traverse through block_tree looking for LocalVariableDeclaration
    # we don't go past another Block, though
    
    res = []

    for c in block_tree.children:
        if c == Node('LocalVariableDeclaration'):
            res.append(c)
        elif c != Node('Block'):
            res.extend(build_variables(c))

    return res

