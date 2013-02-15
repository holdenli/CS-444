#!/usr/bin/python3

import os
import sys

class Node:

    def __init__(self, name=None, value=None, children=None):
        if children == None:
            children = []
        
        self.name = name
        self.value = value
        self.children = children

    def __repr__(self):
        return "<Node: %s=%s>" % (self.name, self.value)

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.name == other.name
        
        return False

    def find_child(self, token_name):
        i = self.children.index(Node(token_name))
        if i != -1:
            return self.children[i]
        return None;

    def bfs_iter(self, leafs=False, filterfn=None):
        queue = [self]
        while len(queue) > 0:
            node = queue.pop(0)
            queue += node.children
            if leafs and len(node.children) != 0:
                continue

            yield node

    def dfs_iter(self, leafs=False, filterfn=None):
        stack = [self]
        while len(stack) > 0:
            node = stack.pop(0)
            stack = node.children + stack
            if leafs and len(node.children) != 0:
                continue

            yield node

    def leafs(self):
        return list(self.dfs_iter(True))

    def select(self, names, deep=False):
        """
        self.select(['ClassDeclaration', 'Modifiers'])
        
        will search through this node's heirarchy and return a list of all
        'Modifiers' nodes that have a ClassDeclaration->Modifiers structure
        in this node's subtree.
        
        """
        stack = [self]
        stack_counters = [0]
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
            
            stack = node.children + stack
            stack_counters = [node_counter]*len(node.children) + stack_counters

    def pprint(self, tabsize=0):
        print(' '*tabsize, self, self.value)
        for c in self.children:
            c.pprint(tabsize=tabsize+2)

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

