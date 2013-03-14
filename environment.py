
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
    cls = list(env.select(['ClassDeclaration']))
    iface = list(env.select(['InterfaceDeclaration']))

    if cls:
        return cls[0].node
    elif iface:
        return iface[0].node
    else:
        return None

def env_type_name(env):

    cls = list(env.select(['ClassDeclaration']))
    iface = list(env.select(['InterfaceDeclaration']))

    if cls:
        name = cls[0].node.select_leaf_values(['ClassName', 'Identifier'])[0]
    elif iface:
        name = iface[0].node.select_leaf_values(['InterfaceName', 'Identifier'])[0]
    else:
        return None

    return name

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

def build_environment(abs_tree):
    """
        environment stack:

        - PackageDeclaration
        - CompilationUnit
            - TypeImports
            - PackageImports
    """

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
    cls = list(abs_tree.select(['ClassDeclaration']))
    iface = list(abs_tree.select(['InterfaceDeclaration']))
    if len(cls) > 0:
        cu.children.append(build_class_env(cls[0]))
    if len(iface) > 0:
        cu.children.append(build_interface_env(iface[0]))

    # add the CompilationUnit to the package
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

            # get the parameters
            params = build_method_params(method_node)
            
            method_env = build_block_env(method_node, set(params))
            if len(method_env) > 0:
                # add the params into the root method_env
                method_env[0].names.update(params)
                env.children.extend(method_env)

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

    for block in find_nodes(tree, [Node('Block'), Node('ForStatement')]):
        # get all the variables in this environment
        env = Environment(name='Block')
        env.node = block
        block.env = env # the block should point back to the env
        
        new_carry = set(carry)

        if block == Node('ForStatement'):
            
            # block[0] is ForInit
            # block[0][0] is LocalVariableDeclaration
            # block[0][0][1] is Identifier for LocalVariableDecl
            # block[3] is ForBody
            for_vars = list(block.select(['ForStatement', 'ForInit',
                'LocalVariableDeclaration']))

            if len(for_vars) != 0:
                name = for_vars[0][1].value.value
                if name in new_carry:
                    logging.error("No two local variables=%s with overlapping scope have the same name"
                        % name)
                    sys.exit(42)

                env.names[name] = for_vars[0]
                new_carry.add(name)

            env.children.extend(build_block_env(block[3], new_carry))
        else:
            for stmt in find_nodes(block, [Node('Block'), Node('ForStatement'),
                Node('LocalVariableDeclaration')]):

                # are we making a new block?
                if stmt == Node('Block') or stmt == Node('ForStatement'):
                    env.children.extend(build_block_env(block, new_carry))

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

def find_nodes(block_tree, white_list):
    # we traverse through block_tree looking for LocalVariableDeclaration
    # we don't go past another Block, though
    ret = []
    for c in block_tree.children:
        if c in white_list:
            ret.append(c)
        else:
            ret.extend(find_nodes(c, white_list))

    return ret
