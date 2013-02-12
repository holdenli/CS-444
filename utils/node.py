#!/usr/bin/python3

import os
import sys

class Node:

    name = None
    token = None
    children = []

    def __init__(self, n=None, t=None, c=[]):
        self.name = n
        self.token = t
        self.children = c

    def __repr__(self):
        return "<Node: %s>" % (self.name)

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
        return list(self.dfs_iter(True))

if __name__ == "__main__":
    n = Node("OMG1",
        c=[
            Node("1", c=[Node("A", c=[Node("C", ("token"))])]),
            Node("2"),
            Node("3", c=[Node("B", ("token"))])
            ])
    print("BFS")
    print(list(n.bfs_iter()))
    print(list(n.bfs_iter(True)))
    print("DFS")
    print(list(n.dfs_iter()))
    print(list(n.dfs_iter(True)))

