#!/usr/bin/python3

class Node:

    def __init__(self, name=None, value=None, children=None, env=None):
        if children == None:
            children = []
        
        self.name = name
        self.value = value
        self.children = children
        self.env = env

    def __repr__(self):
        if self.value != None:
            return "<Node: %s=%s>" % (self.name, self.value)
        else:
            return "<Node: %s>" % (self.name)

    def __eq__(self, other):
        return (other.__class__ == ASTNode or other.__class__ == Node) and (self.name == other.name)

    def __getitem__(self, key):
        return self.children[key]

    def find_child(self, token_name):
        for child in self.children:
            if child.name == token_name:
                return child
        return None

    def add(self, node):
        """
        Adds node to children (mostly for convenience).
        """
        self.children.append(node)

    @property
    def first(self):
        """
        Convenience getter for the first child.
        """
        return self.children[0]

    def bfs_iter(self, leafs=False):
        queue = [self]
        while len(queue) > 0:
            node = queue.pop(0)
            queue += node.children
            if leafs and len(node.children) != 0:
                continue

            yield node

    def dfs_iter(self, leafs=False):
        stack = [self]
        while len(stack) > 0:
            node = stack.pop(0)
            stack = node.children + stack
            if leafs and len(node.children) != 0:
                continue

            yield node

    def leafs(self):
        return list(self.dfs_iter(leafs=True))

    def leaf_values(self):
        return [l.value.value for l in self.leafs()]

    def select(self, names, deep=False, inclusive=True):
        """
        self.select(['ClassDeclaration', 'Modifiers'])
        
        will search through this node's heirarchy and return a list of all
        'Modifiers' nodes that have a ClassDeclaration->Modifiers structure
        in this node's subtree.
        
        """
        if inclusive:
            stack = [self]
            stack_counters = [0]
        else:
            stack = list(self.children)
            stack_counters = [0] * len(self.children)

        while len(stack) > 0:
            node = stack.pop(0)
            node_counter = stack_counters.pop(0)

            if node.name == names[node_counter]:
                node_counter += 1
                if node_counter == len(names):
                    yield node

                    if deep:
                        node_counter = 0
                    else:
                        continue
            else:
                node_counter = 0

            try:
                stack = node.children + stack
            except:
                print(stack)
                print(node, type(node.children))
                node.pprint()

            stack_counters = [node_counter]*len(node.children) + stack_counters

    def select_leaf_values(self, names):
        ret = []
        for s in self.select(names):
            ret.extend(i.value.value for i in s.leafs())

        return ret

    def pprint(self, tabsize=0):
        print(' '*tabsize, self)
        for c in self.children:
            c.pprint(tabsize=tabsize+2)

class ASTNode(Node):

    # Reference to a Type declaration.
    typ = None

    # Store a reference to a declaration (field, method, parameter, or local
    # variable) node. Only valid for certain types of expressions.
    decl = None

    def __init__(self, name=None, value=None, children=None, env=None):
        super().__init__(name, value, children, env)

    def set_typ(node):
        pass

    def set_decl(node):
        pass
        

if __name__ == "__main__":
    n = Node("OMG1",
        children=[
            Node("1", children=[Node("A", children=[Node("C", ("token"))])]),
            Node("2"),
            Node("3", children=[Node("B", ("token"))])
            ])
    print("BFS")
    print(list(n.bfs_iter()))
    print(list(n.bfs_iter(True)))
    print("DFS")
    print(list(n.dfs_iter()))
    print(list(n.dfs_iter(True)))

