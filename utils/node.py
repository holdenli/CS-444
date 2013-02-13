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
        return "<Node: %s>" % (self.name)

    def bfs_iter(self, leafs=False, filterfn=None):
        queue = [self]
        while len(queue) > 0:
            node = queue.pop(0)
            queue += node.children
            if leafs and len(node.children) != 0:
                continue

            if filterfn and not filterfn(node.name, node.value):
                continue

            yield node

    def dfs_iter(self, leafs=False, filterfn=None):
        stack = [self]
        while len(stack) > 0:
            node = stack.pop(0)
            stack = node.children + stack
            if leafs and len(node.children) != 0:
                continue

            if filterfn and not filterfn(node.name, node.value):
                continue

            yield node

    def leafs(self):
        return list(self.dfs_iter(True))

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

